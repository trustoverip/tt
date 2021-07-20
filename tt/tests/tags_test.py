from ..tag import normalize


def test_normalize_forces_lower_case():
    assert normalize('#TEST') == '#test'


def test_normalize_forces_hyphens():
    assert normalize('#two_words') == '#two-words'