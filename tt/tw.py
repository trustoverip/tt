import os
import re
import subprocess
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
                    complete_path = os.path.join(self.folder, root, f)
                    yield Page(os.path.relpath(self.folder, complete_path), self)


class Page:
    def __init__(self, path, wiki=None):
        self._wiki = weakref.ref(wiki) if wiki else None
        self.path = os.path.normpath(os.path.abspath(path))
        self._ast = None
        self._sections = None

    @property
    def wiki(self):
        return self._wiki() if self._wiki else None

    @property
    def is_term(self):
        return self.fname not in ['Home.md']

    @property
    def fname(self):
        return os.path.basename(self.path)

    @property
    def term(self):
        return self.fname[:-3]

    @property
    def definition_section(self):
        for item in self.sections:
            if item.fragment == '#definition':
                return item

    @property
    def tags_section(self):
        for item in self.sections:
            if item.fragment == '#tags':
                return item

    @property
    def tags(self):
        ts = self.tags_section
        if ts:
            return TAGS_SPLITTER.split(ts.text)

    @property
    def ast(self):
        if self._ast is None:
            with open(self.path, 'rt') as f:
                self._ast = markdown.parse(f.read())
        return self._ast

    @property
    def sections(self):
        if self._sections is None:
            self._sections = markdown.split(self.ast)
        return self._sections
