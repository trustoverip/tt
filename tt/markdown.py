import marko
import re


def parse(markdown_text):
    """
    Turn markdown text into an abstract syntax tree (AST).
    """
    md = marko.Markdown(renderer=MarkdownRenderer)
    return md.parse(markdown_text)


def render(ast):
    """
    Turn an abstract syntax tree (AST) into markdown text.
    """
    r = MarkdownRenderer()
    return r.render(ast)


def render_html(ast):
    """
    Turn an abstract syntax tree (AST) into html.
    """
    r = marko.HTMLRenderer()
    return r.render(ast)


def walk_hyperlinks(ast):
    if type(ast) is marko.inline.Link:
        yield ast
    elif hasattr(ast, 'children') and ast.children and type(ast.children) is not str:
        for child in ast.children:
            for link in walk_hyperlinks(child):
                yield link


_TAG_PAT = re.compile('<[^>]+>')


def make_hovertext(ast):
    r = marko.HTMLRenderer()
    txt = _TAG_PAT.sub('', r.render(ast))
    i = txt.find('\n')
    if i > -1:
        txt = txt[:i].rstrip()
    i = txt.find('. ')
    if i > -1:
        txt = txt[:i + 1]
    return txt


def split(ast):
    sections = []
    section_children = []
    first_header_level = None
    for child in ast.children:
        if type(child) is marko.block.Heading:
            # Do I already have children? If yes, maybe it's time for
            # this section to be done...
            if section_children:
                # If this new section is a peer or outdent from the
                # last section we were reading...
                if first_header_level is None or (child.level <= first_header_level):
                    sections.append(Section(section_children))
                    section_children = [child]
                else:
                    # Heading indented beneath the current section.
                    section_children.append(child)
            else:
                if first_header_level is None:
                    first_header_level = child.level
                section_children.append(child)
        else:
            section_children.append(child)
    if section_children:
        sections.append(Section(section_children))
    return sections


NON_ALPHANUMS_PAT = re.compile('[^a-z0-9]+', re.I)


def title_to_fragment(title):
    return NON_ALPHANUMS_PAT.sub(' ', title.lower()).strip().replace(' ', '-')


class MarkdownRenderer(marko.renderer.Renderer):
    """
    Starting from a parsed markdown AST, render back to markdown all over again.
    This is used when we want to update markdown files; the updates go in the
    AST and then we generate new markdown for it. The round trip is slightly
    lossy, because stylistic choices in markdown (e.g., using * versus - for
    list items, or *...* versus _..._ for bold, are not retained.

    Example::
        with open('sample.md', 'rt') as f:
            md = f.read()

        markdown = marko.Markdown(renderer=MarkdownRenderer)
        ast = markdown.parse(md)
        print(markdown.render(ast))
    """

    def render_paragraph(self, element):
        children = self.render_children(element)
        if element._tight:
            return children
        else:
            return f"{children}\n"

    def render_list(self, element):
        if element.ordered:
            self.list_item_token = '1. '
        else:
            self.list_item_token = '* '
        return "{children}\n".format(
            children=self.render_children(element)
        )

    def render_list_item(self, element):
        return "{}{}\n".format(self.list_item_token, self.render_children(element))

    def render_quote(self, element):
        return "> {}".format(self.render_children(element))

    def render_fenced_code(self, element):
        lang = (
            element.lang
            if element.lang
            else ""
        )
        return "```{}\n{}```\n".format(
            lang, element.children[0].children
        )

    def render_code_block(self, element):
        return self.render_fenced_code(element)

    def render_html_block(self, element):
        return element.children

    def render_thematic_break(self, element):
        return "<hr />\n"

    def render_heading(self, element):
        return '#' * element.level + " {children}\n".format(
            children=self.render_children(element)
        )

    def render_setext_heading(self, element):
        return self.render_heading(element)

    def render_blank_line(self, element):
        return "\n"

    def render_link_ref_def(self, element):
        return ""

    def render_emphasis(self, element):
        return "*{}*".format(self.render_children(element))

    def render_strong_emphasis(self, element):
        return "**{}**".format(self.render_children(element))

    def render_inline_html(self, element):
        return self.render_html_block(element)

    def render_plain_text(self, element):
        if isinstance(element.children, str):
            return element.children
        return self.render_children(element)

    def render_link(self, element):
        return '[{}]({})'.format(self.render_children(element), element.dest)

    def render_auto_link(self, element):
        return self.render_link(element)

    def render_image(self, element):
        template = '![{}]({})'
        render_func = self.render
        self.render = self.render_plain_text
        body = self.render_children(element)
        self.render = render_func
        return template.format(body, element.dest)

    def render_literal(self, element):
        return self.render_raw_text(element)

    def render_raw_text(self, element):
        return element.children

    def render_line_break(self, element):
        if element.soft:
            return "\n"
        return "<br />\n"

    def render_code_span(self, element):
        return "`{}`".format(element.children)


class Section(marko.block.BlockElement):

    @classmethod
    def match(cls, source):
        pass

    def __init__(self, children):
        self.link_ref_defs = {}
        self.children = children
        self._title = None
        self._text = None
        self._content = None

    @property
    def heading(self):
        for child in self.children:
            if type(child) is marko.block.Heading:
                return child

    @property
    def title(self):
        if self._title is None:
            md = MarkdownRenderer()
            self._title = md.render_children(self.heading)
        return self._title

    @property
    def content(self):
        if self._content is None:
            for i in range(len(self.children)):
                child = self.children[i]
                if type(child) is marko.block.Heading:
                    self._content = Section(self.children[i + 1:])
        return self._content

    @property
    def text(self):
        if self._text is None:
            md = MarkdownRenderer()
            self._text = md.render_children(self.content)
        return self._text

    @property
    def fragment(self):
        return title_to_fragment(self.title)

    @property
    def text(self):
        return render(self.content)

    def __str__(self):
        return '# %s\n%s' % (self.title, self.text)



if __name__ == '__main__':
    import os
    with open(os.path.join(os.path.dirname(__file__), 'tests/sample-page.md'), 'rt') as f:
        text = f.read()

    markdown = marko.Markdown(renderer=MarkdownRenderer)
    ast = markdown.parse(text)
    print(markdown.render(ast))