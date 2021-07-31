import io
import re

from . import tw
from . import markdown


import os
with open(os.path.join(os.path.dirname(__file__), 'default.css'), 'rt') as f:
    DEFAULT_CSS = '  <style>\n%s\n  </style>\n' % f.read()
del os

WIKI_PAGE_LINK_PAT = re.compile(r'[a-z0-9]+(-[a-z0-9]+)*$', re.IGNORECASE)


class Source:
    def __init__(self, cfg):
        self.wiki = tw.TermsWiki(cfg.get('wiki'))
        self.tags = cfg.get('tags', None)
        self.adopt = cfg.get('adopt', False)


class Glossary:
    def __init__(self, cfg):
        self._title = cfg.get('title')
        self.css = cfg.get('css')
        sources = cfg.get('sources')
        self._sources = []
        for source in sources:
            self._sources.append(Source(source))
        self._pages = None

    @property
    def is_standalone_doc(self):
        return self.title or self._css

    @property
    def title(self):
        return self._title if self._title else "Glossary"

    @property
    def sources(self):
        return self._sources

    @property
    def pages(self):
        if self._pages is None:
            self._pages = []
            for source in self._sources:
                for page in source.wiki.pages:
                    if page.is_term:
                        self._pages.append(page)
        self._pages.sort(key=lambda p: p.fragment)
        return self._pages

    @property
    def primary_source(self):
        return self._sources[0] if self._sources else None

    def handle_synonyms(self):
        # Make a copy of pages list that I can iterate safely
        # while I'm changing the other list.
        pages = self.pages[:]
        for page in pages:
            twin = None
            if page.acronym:
                twin = page.make_acronym_twin()
                self._pages.append(twin)
        self._pages.sort(key=lambda p: p.fragment)

    def fix_hyperlinks(self):
        for page in self.pages:
            for link in markdown.walk_hyperlinks(page.ast):
                if WIKI_PAGE_LINK_PAT.match(link.dest):
                    link.dest = '#' + link.dest

    def render(self):
        self.handle_synonyms()
        self.fix_hyperlinks()
        out = io.StringIO()
        if self.is_standalone_doc:
            out.write("<html>\n<head>\n")
            out.write("  <title>%s</title>\n" % self.title)
            if self.css:
                out.write('  <link rel="stylesheet" href="%s">\n' % self.css)
            else:
                out.write(DEFAULT_CSS)
            out.write("</head>\n<body>\n<header>%s</header>\n<main>\n" % self.title)
        out.write("<dl>")
        for page in self.pages:
            out.write('\n<dt id="%s">%s</dt>\n' % (page.fragment, page.term_minus_acronym))
            this_def = page.get_section_by_fragment('definition')
            if this_def:
                out.write("<dd>%s</dd>\n" % markdown.render_html(this_def.content))
        out.write("</dl>\n")
        if self.is_standalone_doc:
            out.write("</main>\n</body>\n</html>\n")
        out.seek(0)
        return out.read()

