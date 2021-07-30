import os
import re

from ..  import markdown

THIS_FOLDER = os.path.dirname(os.path.abspath(__file__))
SAMPLE_PAGE_PATH = os.path.join(THIS_FOLDER, 'sample-page.md')
with open(SAMPLE_PAGE_PATH, 'rt') as f:
    SAMPLE_PAGE = f.read()


def test_round_trip():
    ast = markdown.parse(SAMPLE_PAGE)
    output = markdown.render(ast)

    # Sample page has a few stylistic choices in it that are undone
    # by rendering. Eliminate these before comparing.
    input = SAMPLE_PAGE.replace(
        '>Note', '> Note').replace(
        '_bolded_', '*bolded*').replace(
        '2.', '1.')

    # There are some differences between line spacing with list items
    # in the two versions of the text. Remove these as well.
    def norm_lines(x):
        return re.sub('\n{2,}', '\n', x)

    input = norm_lines(input)
    output = norm_lines(output)

    #with open('x.txt', 'wt') as f:
    #    f.write(input)
    #with open('y.txt', 'wt') as f:
    #    f.write(output)
    assert input == output


def test_section():
    ast = markdown.parse(SAMPLE_PAGE)
    sections = markdown.split(ast)
    assert len(sections) == 4

    # first section
    s = sections[0]
    assert s.title == "Definition"
    assert s.fragment == '#definition'
    assert re.compile(r".*?common context.*?disambiguates.*?Note:.*?[*]italic",
                      re.MULTILINE + re.DOTALL).search(s.text)
    assert 'Example' not in s.text
    assert 'Another bulleted item' not in s.text

    # skip second section

    # third section
    s = sections[2]
    assert s.title == 'Notes'
    assert re.compile(r'`conventions`.*identified by a tag.*terminology',
                      re.MULTILINE + re.DOTALL).search(s.text)
    assert '#tag2' not in s.text

    # fourth section
    s = sections[3]
    assert s.fragment == '#tags'
    assert '#tag3' in s.text


if __name__ == '__main__':
    test_section()