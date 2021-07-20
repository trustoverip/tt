import re

from .tag import normalize

git_repo_pat = re.compile('git@github.com:([^/]+)/(.*?)(?:[.]wiki)?[.]git$')
https_repo_pat = re.compile('https://github.com/([^/]+)/(.*?)(?:[.]wiki)?[.]git$')
tag_pat = re.compile('(.*)[_-]terms$', re.I)


class TermsWiki:
    def __init__(self, which):
        m = git_repo_pat.match(which)
        if not m:
            m = https_repo_pat.match(which)
        if m:
            self.github_user = m.group(1)
            self.repo_name = m.group(2)
        else:
            self.github_user = 'trustoverip'
            self.repo_name = which
        m = tag_pat.match(self.repo_name)
        self.tag = normalize(m.group(1) if m else self.repo_name)

    @property
    def uri(self):
        return 'http://github.com/%s/%s.wiki.git' % (self.github_user, self.repo_name)
