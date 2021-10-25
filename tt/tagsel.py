import re


from .tag import normalize


class BadExpression(Exception):
    def __init__(self, txt):
        Exception.__init__(self, txt)


def _negate(txt, negated):
    return "NOT " + txt if negated else txt


class BinaryExpr():
    def __init__(self, lhs=None, operator=None):
        self.negated = False
        self.lhs = lhs
        self.operator = operator
        self.rhs = None

    def __str__(self):
        return _negate("%s %s %s" % (self.lhs, self.operator.upper(), str(self.rhs)), self.negated)

    def matches(self, tags):
        lhs_matches = self.lhs.matches(tags)
        rhs_matches = self.rhs.matches(tags)
        combo = bool(lhs_matches and rhs_matches) if self.operator == 'and' else bool(lhs_matches or rhs_matches)
        return combo != self.negated


class ValueExpr():
    def __init__(self, value=None):
        self.negated = False
        self.value = value

    def __str__(self):
        return _negate(self.value, self.negated)

    def matches(self, tags):
        return (self.value in tags) != self.negated


class GroupedExpr():
    def __init__(self, expr):
        self.negated = False
        self.expr = expr

    def __str__(self):
        return _negate('(%s)' % str(self.expr), self.negated)

    def matches(self, tags):
        return self.expr.matches(tags) != self.negated


"""Parser expects an expression; will be satisfied by group or tag, will allow 'not'."""
NEED_EXPR = 0
"""Parser has an expression; will only allow 'and' or 'or' to extend."""
EXTENDING_EXPR = 1
"""Parser is waiting while a parenthesized subexpression is being parsed."""
IN_PARENS = 2


class Parser:
    def __init__(self, parent = None):
        self.parent = parent
        self.expr = None
        self.negate_next = False
        self.subparser = None
        self._transition_to(NEED_EXPR)

    def _assign_expr(self, expr):
        self.expr = expr
        self.expr.negated = self.negate_next
        self.negate_next = False

    @property
    def trailing_rhs(self):
        x = self.expr
        while isinstance(x, BinaryExpr):
            if x.rhs is None:
                return x
            x = x.rhs

    def _update_expr(self, expr=None, operator=None):
        """
        React to newly parsed info about the current expression.
        """
        if self.expr is None:
            self._assign_expr(expr)
        else:
            if isinstance(self.expr, ValueExpr) or isinstance(self.expr, GroupedExpr):
                self._assign_expr(BinaryExpr(self.expr, operator))
            elif isinstance(self.expr, BinaryExpr):
                trailing_rhs = self.trailing_rhs
                if trailing_rhs:
                    trailing_rhs.rhs = expr
                    trailing_rhs.rhs.negated = self.negate_next
                    self.negate_next = False
                else:
                    # We have to compare the old binary operator to the new one. If new is
                    # 'and' and old is 'or', then we need to rebind to honor the greater
                    # precedence of 'and'. Example:
                    #     #a or #b and #c
                    #     ^------^________initial grouping into BinaryExpr
                    #              ^______should cause #b to rebind with #c
                    if operator == 'and' and self.expr.operator == 'or':
                        self.expr.rhs = BinaryExpr(self.expr.rhs, operator)
                    else:
                        self._assign_expr(BinaryExpr(self.expr, operator))

    def _transition_to(self, new_state):
        self.state = new_state
        if new_state == NEED_EXPR:
            self.on_token_func = self._on_while_need
        elif new_state == EXTENDING_EXPR:
            self.on_token_func = self._on_while_ext
        elif new_state == IN_PARENS:
            self.on_token_func = self._on_while_in_parens
        else:
            assert False == 'implemented'

    def on_token(self, token):
        """
        Process another token.
        """
        if self.subparser:
            self.subparser.on_token(token)
        else:
            self.on_token_func(token)

    def _on_while_in_parens(self, token):
        """
        Handle token in the IN_PARENS state.
        """
        if token == ')':
            self.update_expr(self.subparser.expr)
            self.subparser.parent = None
            self.subparser = None
            self._transition_to(EXTENDING_EXPR)
        else:
            raise BadExpression('Unexpected token "%s" when expecting open or close paren.' % token)

    def _on_while_need(self, token):
        """
        Handle token in the NEED_EXPR state (no meaningful content seen yet).
        """
        if token == '(':
            # Handle grouping by recursing and passing parsing responsibility to
            # a parser for the subexpression.
            self.subparser = Parser(self)
            self._transition_to(IN_PARENS)
        elif token == 'not':
            self.negate_next = not self.negate_next
        elif token.startswith('#'):
            token = normalize(token)
            if len(token) == 1:
                raise BadExpression('Invalid tag.')
            self._update_expr(ValueExpr(token))
            self._transition_to(EXTENDING_EXPR)
        else:
            raise BadExpression('Unexpected token "%s".' % token)

    def _on_while_ext(self, token):
        """
        Handle token in the EXTEND_EXPR state.
        """
        if token in ['and', 'or']:
            self._update_expr(operator=token)
            self._transition_to(NEED_EXPR)
        elif token == ')':
            p = self.parent
            if not p:
                raise BadExpression("Unexpected close paren.")
            p._update_expr(GroupedExpr(self.expr))
            # Do I have to transfer negation by checking whether internal and external negation are different?
            p.subparser = self.parent = None
            p._transition_to(EXTENDING_EXPR)
        else:
            raise BadExpression('Unexpected token "%s".' % token)


_TOKEN_SEPARATOR = re.compile('[ \t\r\n]+')


def parse(expr):
    # Make sure operators are lower case and that parens are
    # separated from any tokens they touch.
    expr = expr.lower().replace('(', ' ( ').replace(')', ' ) ').strip()
    tokens = _TOKEN_SEPARATOR.split(expr)
    parser = Parser()
    for token in tokens:
        parser.on_token(token)
    if parser.state == IN_PARENS:
        raise BadExpression("Missing close paren.")
    elif parser.state != EXTENDING_EXPR:
        raise BadExpression("Incomplete expression.")
    return parser.expr

