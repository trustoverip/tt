from . import tw
from . import markdown


class Source:
    def __init__(self, cfg):
        self.wiki = tw.TermsWiki(cfg.get('wiki'))
        self.tags = cfg.get('tags', None)
        self.adopt = cfg.get('adopt', False)


class Glossary:
    def __init__(self, cfg):
        self.title = cfg.get('title')
        self.css = cfg.get('css')
        sources = cfg.get('sources')
        self._sources = []
        for source in sources:
            self._sources.append(Source(source))
        self._pages = None

    @property
    def is_standalone_doc(self):
        return self.title or self.css

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
        self._pages.sort(key=lambda p: page.fragment)
        return self._pages

    @property
    def primary_source(self):
        return self._sources[0] if self._sources else None

    def write(self, out):
        if self.is_standalone_doc:
            out.write("<html>\n<head>\n")
            if self.title:
                out.write("  <title>%s</title>\n" % self.title)
            if self.css:
                out.write('  <link rel="stylesheet" href="%s">\n' % self.css)
            out.write("</head>\n<body>\n")
        out.write("<dl>\n")
        for page in self.pages:
            out.write('\n<dt id="%s">%s</dt>\n' % (page.fragment, page.term))
            this_def = page.get_section_by_fragment('definition')
            if this_def:
                out.write("<dd>%s</dd>\n" % markdown.render_html(this_def.content))
        out.write("</dl>\n")
        if self.is_standalone_doc:
            out.write("</body>\n</html>\n")



