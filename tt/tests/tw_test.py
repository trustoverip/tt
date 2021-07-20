from ..tw import *


def test_short_parseable():
    ctwg = TermsWiki('ctwg-terms')
    assert ctwg.code_repo_name == 'ctwg-terms'
    assert ctwg.repo_name == 'ctwg-terms.wiki'
    assert ctwg.github_user == 'trustoverip'
    assert ctwg.tag == '#ctwg'
    assert ctwg.repo_url == 'http://github.com/trustoverip/ctwg-terms.wiki.git'


def test_git_code_parseable():
    ctwg = TermsWiki('git@github.com:foo/someones_terms.git')
    assert ctwg.code_repo_name == 'someones_terms'
    assert ctwg.repo_name == 'someones_terms.wiki'
    assert ctwg.github_user == 'foo'
    assert ctwg.tag == '#someones'
    assert ctwg.repo_url == 'http://github.com/foo/someones_terms.wiki.git'
