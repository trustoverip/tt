import os
import re

from .tag import normalize

GIT_REPO_PAT = re.compile('git@github.com:([^/]+)/(.*?)(?:[.]wiki)?[.]git$')
HTTPS_REPO_PAT = re.compile('https://github.com/([^/]+)/(.*?)(?:[.]wiki)?[.]git$')
TAG_PAT = re.compile('(.*)[_-]terms$', re.I)
LOCAL_PATH = os.path.normpath(os.path.expanduser('~/.tt/corpus'))
WIKI_SUFFIX = '.wiki'


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

    @property
    def code_repo_url(self):
        return 'http://github.com/%s/%s.git' % (self.github_user, self.code_repo_name)

    @property
    def repo_url(self):
        return 'http://github.com/%s/%s.git' % (self.github_user, self.repo_name)

    @property
    def folder(self):
        return os.path.join(LOCAL_PATH, self.repo_name)

    @property
    def exists_locally(self):
        return os.path.isdir(self.folder)
