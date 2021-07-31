import os
import pytest
import tempfile

from .. import tw

SAMPLE_PAGE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'sample-page.md')


def test_short_parseable():
    ctwg = tw.TermsWiki('ctwg-terms')
    assert ctwg.code_repo_name == 'ctwg-terms'
    assert ctwg.repo_name == 'ctwg-terms.wiki'
    assert ctwg.github_user == 'trustoverip'
    assert ctwg.tag == '#ctwg'
    assert ctwg.repo_url == 'https://github.com/trustoverip/ctwg-terms.wiki.git'


def test_git_code_parseable():
    ctwg = tw.TermsWiki('git@github.com:foo/someones_terms.git')
    assert ctwg.code_repo_name == 'someones_terms'
    assert ctwg.repo_name == 'someones_terms.wiki'
    assert ctwg.github_user == 'foo'
    assert ctwg.tag == '#someones'
    assert ctwg.repo_url == 'https://github.com/foo/someones_terms.wiki.git'


@pytest.fixture
def scratch_space():
    x = tempfile.TemporaryDirectory()
    old_local_path = tw.LOCAL_PATH
    tw.LOCAL_PATH = x.name
    yield x
    tw.LOCAL_PATH = old_local_path
    x.cleanup()


def test_clone(scratch_space):
    x = tw.TermsWiki(tw.SAMPLE_TERMS_WIKI_REPO)
    x.refresh()
    assert len(os.listdir(x.folder)) > 1


def test_refresh(scratch_space):
    x = tw.TermsWiki(tw.SAMPLE_TERMS_WIKI_REPO)
    x.refresh()
    os.chdir(x.folder)
    # Reset state of repo to something that lacked the parsec.md file.
    os.system('git reset --hard e3a6c5b82b718e202f5b547c1361344254ff6914')
    assert not os.path.exists('parsec.md')
    x.refresh(force=True)
    # If refresh worked, we should now have the parsec.md file.
    assert os.path.isfile('parsec.md')


def test_pages_iter(scratch_space):
    x = tw.TermsWiki(tw.SAMPLE_TERMS_WIKI_REPO)
    pages = [p for p in x.pages]
    assert len(pages) >= 3


def test_page():
    page = tw.Page(SAMPLE_PAGE)
    assert page.is_term
    assert page.term == "sample-page"
    assert "#tag1" in page.tags


if __name__ == '__main__':
    test_page()
