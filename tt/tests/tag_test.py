from ..tag import normalize, edit_distance


def test_normalize_forces_lower_case():
    assert normalize('#TEST') == '#test'


def test_normalize_forces_hyphens():
    assert normalize('#two_words') == '#two-words'


def test_edit_distance():
    assert edit_distance("hello-world", 'HelloWorld') == 0