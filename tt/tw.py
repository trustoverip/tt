import weakref

from .tag import normalize
from .git import *
from . import markdown

GIT_REPO_PAT = re.compile('git@github.com:([^/]+)/(.*?)(?:[.]wiki)?[.]git$')
HTTPS_REPO_PAT = re.compile('https://github.com/([^/]+)/(.*?)(?:[.]wiki)?[.]git$')
TAG_PAT = re.compile('(.*)[_-]terms$', re.I)
LOCAL_PATH = os.path.normpath(os.path.expanduser('~/.tt/corpus'))
WIKI_SUFFIX = '.wiki'
SAMPLE_TERMS_WIKI_REPO = 'git@github.com:dhh1128/scifi-terms.git'
TAGS_SPLITTER = re.compile(r'[* \t\r\n,]+')
ACRONYM_PAT = re.compile(r'(.*?)\s*\(([^)]+)\)$')


class TermsWiki:
    def __init__(self, which):
        m = GIT_REPO_PAT.match(which)
        if not m:
            m = HTTPS_REPO_PAT.match(which)
        if m:
            self.github_user = m.group(1)
            name = m.group(2)
        else:
            self.github_user = 'trustoverip'
            name = which
        if name.endswith(WIKI_SUFFIX):
            self.repo_name = name
            self.code_repo_name = name[:-1 * WIKI_SUFFIX.len()]
        else:
            self.code_repo_name = name
            self.repo_name = name + WIKI_SUFFIX
        m = TAG_PAT.match(self.code_repo_name)
        self.tag = normalize(m.group(1) if m else self.code_repo_name)
        self.refreshed = False

    @property
    def code_repo_url(self):
        return 'https://github.com/%s/%s.git' % (self.github_user, self.code_repo_name)

    @property
    def repo_url(self):
        return 'https://github.com/%s/%s.git' % (self.github_user, self.repo_name)

    @property
    def folder(self):
        return os.path.join(LOCAL_PATH, self.repo_name)

    @property
    def is_cloned(self):
        return os.path.isdir(self.folder)

    def refresh(self, force=False):
        if force or (not self.refreshed):
            self.refreshed = True
            if not self.is_cloned:
                clone(self.repo_url, self.folder)
            else:
                pull(self.folder)

    @property
    def pages(self):
        self.refresh()
        for root, folders, files in os.walk(self.folder):
            if '.git' in folders:
                folders.remove('.git')
            for f in files:
                if f.endswith('.md'):
                    yield Page(os.path.join(root, f), self)


class Page:
    def __init__(self, path, wiki=None):
        self._wiki = weakref.ref(wiki) if wiki else None
        self.path = os.path.normpath(os.path.abspath(path))
        self._ast = None
        self._sections = None
        self.term = self.fname[:-3].replace('-', ' ')
        self._hovertext = None
        self._history = None

    @property
    def wiki(self):
        return self._wiki() if self._wiki else None

    @property
    def is_term(self):
        return self.get_section_by_fragment('definition') or self.get_section_by_fragment('see')

    @property
    def acronym(self):
        m = ACRONYM_PAT.match(self.term)
        return m.group(2) if m else None

    @property
    def term_minus_acronym(self):
        m = ACRONYM_PAT.match(self.term)
        return m.group(1) if m else self.term

    @property
    def fname(self):
        return os.path.basename(self.path)

    @property
    def fragment(self):
        return markdown.title_to_fragment(self.term)

    @property
    def hovertext(self):
        if self._hovertext is None:
            self._hovertext = ""
            dfn = self.get_section_by_fragment('definition')
            if dfn:
                for child in dfn.children:
                    if type(child) is markdown.marko.block.Paragraph:
                        self._hovertext = markdown.make_hovertext(child)
                        break
        return self._hovertext

    def get_section_by_fragment(self, fragment):
        for item in self.sections:
            h = item.heading
            if h:
                if item.fragment == fragment:
                    return item

    @property
    def tags(self):
        x = []
        w = self.wiki
        if w:
            x.append(w.tag)
        ts = self.get_section_by_fragment('tags')
        if ts:
            term_specific_tags = TAGS_SPLITTER.sub(' ', ts.text).strip()
            if term_specific_tags:
                x += term_specific_tags.split(' ')
        x.sort()
        return x

    @property
    def ast(self):
        if self._ast is None:
            with open(self.path, 'rt') as f:
                self._ast = markdown.parse(f.read())
        return self._ast

    @property
    def history(self):
        if self._history is None:
            try:
                self._history = get_history(self.path)
            except:
                self._history = []
        return self._history

    @property
    def version(self):
        return len(self._history) if self.history else 0

    @property
    def hash(self):
        return self._history[0][:7] if self.history else 0

    @property
    def creation_date(self):
        if self.history:
            return int(self._history[-1][self._history[-1].rfind(',') + 1:])

    @property
    def lastmod_date(self):
        if self.history:
            return int(self._history[0][self._history[0].rfind(',') + 1:])

    @property
    def contributors(self):
        if self.history:
            c = []
            for event in self._history:
                i = event.find(',')
                j = event.rfind(',')
                person = event[i+1:j]
                if person not in c:
                    c.append(person)
            return c

    @property
    def sections(self):
        if self._sections is None:
            self._sections = markdown.split(self.ast)
        return self._sections
