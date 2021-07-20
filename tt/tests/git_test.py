from ..git import *


def test_is_installed():
    assert VERSION_PAT.match(is_installed())