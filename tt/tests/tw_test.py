from ..tw import *

def test_ctwg_parseable():
    ctwg = TermsWiki('ctwg-terms')
    assert ctwg.repo_name == 'ctwg-terms'
    assert ctwg.github_user == 'trustoverip'
    assert ctwg.tag == '#ctwg'
    assert ctwg.uri == 'http://github.com/trustoverip/ctwg-terms.wiki.git'


