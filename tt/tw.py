import os
import re
import subprocess

from .tag import normalize
from .git import *

GIT_REPO_PAT = re.compile('git@github.com:([^/]+)/(.*?)(?:[.]wiki)?[.]git$')
HTTPS_REPO_PAT = re.compile('https://github.com/([^/]+)/(.*?)(?:[.]wiki)?[.]git$')
TAG_PAT = re.compile('(.*)[_-]terms$', re.I)
LOCAL_PATH = os.path.normpath(os.path.expanduser('~/.tt/corpus'))
WIKI_SUFFIX = '.wiki'
SAMPLE_TERMS_WIKI_REPO = 'git@github.com:dhh1128/scifi-terms.git'


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

