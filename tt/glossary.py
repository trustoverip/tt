import datetime
import io
import re
import sys

from . import tw
from . import markdown
from . import tagsel


import os
with open(os.path.join(os.path.dirname(__file__), 'default.css'), 'rt') as f:
    DEFAULT_CSS = '  <style>\n%s\n  </style>\n' % f.read()
del os

WIKI_PAGE_LINK_PAT = re.compile(r'[a-z0-9]+(-[a-z0-9]+)*$', re.IGNORECASE)
SHORT_EXTERNAL_GLOSSARY_LINK_PAT = re.compile(r'([a-z0-9]+(?:-[a-z0-9]+)*)@([a-z0-9]+(?:-[a-z0-9]+)*)$', re.IGNORECASE)


class Source:
    def __init__(self, cfg):
        self.wiki = tw.TermsWiki(cfg.get('wiki'))
        self.subset = cfg.get('subset', None)
        if self.subset:
            self.subset = tagsel.parse(self.tags)
        self.adopt = cfg.get('adopt', False)


class Glossary:
    def __init__(self, cfg):
        self._title = cfg.get('title')
        self.css = cfg.get('css')
        self.write_meta = cfg.get('write_meta', True)
        self.frame = cfg.get('frame')
        if self.frame:
            import requests
            r = requests.get(self.frame)
            self.frame = r.text
        sources = cfg.get('sources')
        self._sources = []
        for source in sources:
            self._sources.append(Source(source))
        self._pages = None

    @property
    def is_standalone_doc(self):
        return bool(self._title) or bool(self.css)

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
                        if (source.subset is None) or source.subset.matches(page.tags):
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

    def find_page(self, fragment):
        for page in self.pages:
            if page.fragment == fragment:
                return page

    def fix_hyperlinks(self):
        for page in self.pages:
            for link in markdown.walk_hyperlinks(page.ast):
                if WIKI_PAGE_LINK_PAT.match(link.dest):
                    target_page = self.find_page(link.dest)
                    link.dest = '#' + link.dest
                    if target_page:
                        link.title = target_page.hovertext
                    else:
                        sys.stderr.write('Broken hyperlink to %s in %s.\n' % (link.dest, page.path))
                        sys.stderr.flush()
                else:
                    m = SHORT_EXTERNAL_GLOSSARY_LINK_PAT.match(link.dest)
                    if m:
                        link.dest = 'https://trustoverip.github.io/' + m.group(2) + '/glossary.html#' + m.group(1)

    def render(self):
        self.handle_synonyms()
        self.fix_hyperlinks()

        # Write the pieces of the output to 3 separate buffers so we can build
        # the nav stuff as we process the pages, but order the nav before the
        # main glossary.
        doc = io.StringIO()
        nav = io.StringIO()
        inner = io.StringIO()

        if self.is_standalone_doc:
            doc.write("<html>\n<head>\n")
            doc.write("  <title>%s</title>\n" % self.title)
            if self.css:
                doc.write('  <link rel="stylesheet" href="%s">\n' % self.css)
            else:
                doc.write(DEFAULT_CSS)
            doc.write("</head>\n<body>\n<header>%s</header>\n" % self.title)

        toc = []
        current_char = None
        inner.write("<dl>")
        for page in self.pages:
            try:
                # First term that starts with this letter?
                char = page.fragment[0].upper()
                if char != current_char:
                    current_char = char
                    toc.append(char)
                    inner.write('\n<dt id="%s" class="letter">%s</td>' % (char, char))
                inner.write('\n<dt id="%s"><a href="#%s">%s</a> ' % (page.fragment, page.fragment, page.term_minus_acronym))
                for t in page.tags:
                    inner.write('<span class="tag">%s</span>' % t)
                inner.write('</dt>\n')
                this_def = page.get_section_by_fragment('definition')
                if this_def:
                    inner.write("<dd>%s" % markdown.render_html(this_def.content))
                    if page.history and self.write_meta:
                        cdate = datetime.date.fromtimestamp(page.creation_date).strftime("%Y-%m-%d")
                        inner.write('<p class="meta">version %d, commit %s, created %s, ' % (
                            page.version, page.hash, cdate))
                        if page.version > 1:
                            inner.write('last modified %s, ' %
                                        datetime.date.fromtimestamp(page.lastmod_date).strftime("%Y-%m-%d"))
                        inner.write('contributors %s</p>\n' % ' - '.join(page.contributors))
                    inner.write("</dd>\n")
            except:
                sys.stderr.write('Problem with %s.' % page.path)
                raise
        inner.write("</dl>\n")

        nav.write('<nav>[ ')
        for char in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            if char in toc:
                nav.write('<a href="#%s">%s</a> ' % (char, char))
            else:
                nav.write('%s ' % char)
        nav.write(']</nav>\n')

        if self.is_standalone_doc:
            return doc.getvalue() + nav.getvalue() + "<main>\n" + inner.getvalue() + "</main>\n</body>\n</html>\n"
        elif self.frame:
            return self.frame.replace('%nav', nav.getvalue()).replace('%main', inner.getvalue())
        else:
            return inner.getvalue()
