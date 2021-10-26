import pytest

from ..tagsel import *


def test_parse_simple():
    expr = parse("#x")
    assert str(expr) == "#x"


def assert_error(text_to_parse, contains):
    with pytest.raises(BadExpression, match=contains):
        parse(text_to_parse)


def test_parse_unmatched_close_paren():
    assert_error("#x)", "Unexpected close paren")


def test_parse_unmatched_open_paren():
    assert_error("(#x", "Missing close paren")


def test_parse_non_tag():
    assert_error("not-a-tag", "Unexpected token")


def test_parse_and_without_operand():
    assert_error("#x and", "Incomplete expression")


def test_parse_not():
    expr = parse("not #x")
    assert str(expr) == "NOT #x"


def test_parse_double_not():
    expr = parse("not not #x")
    assert str(expr) == "#x"


def test_parse_triple_not():
    expr = parse("not not not #x")
    assert str(expr) == "NOT #x"


def test_parse_and():
    expr = parse("#x and #y")
    assert str(expr) == "#x AND #y"


def test_parse_or():
    expr = parse("#x or #y")
    assert str(expr) == "#x OR #y"


def test_parse_trivial_group():
    expr = parse("(#x)")
    assert str(expr) == "(#x)"


def test_parse_trailing_group():
    expr = parse("#x and (#y or #z)")
    assert str(expr) == "#x AND (#y OR #z)"


def test_parse_leading_group():
    expr = parse("(#x and #y) or #z")
    assert str(expr) == "(#x AND #y) OR #z"


def test_parse_three():
    expr = parse("#x and #y and #z")
    assert str(expr) == "#x AND #y AND #z"


def test_parse_nest():
    expr = parse("#a and (#b or (#c and #d))")
    assert str(expr) == "#a AND (#b OR (#c AND #d))"


def test_parse_center_group():
    expr = parse("#x and (#a or #b) and #z")
    assert str(expr) == "#x AND (#a OR #b) AND #z"


def test_parse_not_center_group():
    expr = parse("#x and not (#a or #b) and #z")
    assert str(expr) == "#x AND NOT (#a OR #b) AND #z"


def test_parse_lots_of_nots():
    expr = parse("#x and not (#a or not #b) and not #z")
    assert str(expr) == "#x AND NOT (#a OR NOT #b) AND NOT #z"


def test_parse_precedence_of_and():
    expr = parse("#a or #b and #c")
    assert str(expr) == "#a OR #b AND #c"


def make_tags(chars):
    return ['#' + c for c in chars]


def assert_tags_match(tag_chars, expr, expected=True):
    expr = parse(expr)
    tags = make_tags(tag_chars)
    assert expr.matches(tags) == expected


def test_match_simple():
    assert_tags_match("abcx", "#x")
    assert_tags_match("abcx", "#z", False)


def test_match_not():
    assert_tags_match("abcx", "not #x", False)
    assert_tags_match("abcx", "not #z")


def test_match_double_not():
    assert_tags_match("abcx", "not not #x")
    assert_tags_match("abcx", "not not #z", False)


def test_match_triple_not():
    assert_tags_match("abcx", "not not not #x", False)
    assert_tags_match("abcx", "not not not #z")


def test_match_and():
    assert_tags_match("yabcx", "#x and #y")
    assert_tags_match("abcx", "#x and #y", False)


def test_match_or():
    assert_tags_match("yabc", "#x or #y")
    assert_tags_match("abc", "#x or #y", False)


def test_match_trivial_group():
    assert_tags_match("axz", "(#x)")
    assert_tags_match("az", "(#x)", False)


def test_match_trailing_group():
    assert_tags_match("axz", "#x and (#y or #z)")
    assert_tags_match("ayz", "#x and (#y or #z)", False)


def test_match_leading_group():
    assert_tags_match("az", "(#x and #y) or #z")
    assert_tags_match("ax", "(#x and #y) or #z", False)


def test_match_three():
    assert_tags_match("abcxyz", "#x and #y and #z")
    assert_tags_match("abcyz", "#x and #y and #z", False)


def test_match_nest():
    assert_tags_match("ab", "#a and (#b or (#c and #d))")
    assert_tags_match("ac", "#a and (#b or (#c and #d))", False)
    assert_tags_match("acd", "#a and (#b or (#c and #d))")


def test_match_center_group():
    assert_tags_match("azx", "#x and (#a or #b) and #z")
    assert_tags_match("czx", "#x and (#a or #b) and #z", False)
    assert_tags_match("ax", "#x and (#a or #b) and #z", False)


def test_match_not_center_group():
    assert_tags_match("xzw", "#x and not (#a or #b) and #z")
    assert_tags_match("xza", "#x and not (#a or #b) and #z", False)
    assert_tags_match("zw", "#x and not (#a or #b) and #z", False)


def test_match_lots_of_nots():
    assert_tags_match("xaw", "#x and not (not #a and not #b) and not #z")
    assert_tags_match("xaw", "#x and (not #a and not #b) and not #z", False)


def test_match_precedence_of_and():
    assert_tags_match("az", "#a or #b and #c")
    assert_tags_match("bcz", "#a or #b and #c")
    assert_tags_match("abz", "#a and #x or #b and #c", False)
    assert_tags_match("axbz", "#a and #x or #b and #c")
    assert_tags_match("abcz", "#a and #x or #b and #c")
