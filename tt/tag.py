import re

NON_ALPHANUMS_PAT = re.compile('[^a-z0-9]+', re.I)


def normalize(tag):
    """
    Return a canonical version of a tag. All non-alphanumeric chars are replaced with
    a single hyphen. Value is lower-case. Leading and trailing hyphens are trimmed.
    """
    return '#' + NON_ALPHANUMS_PAT.sub(' ', tag.lower()).strip().replace(' ', '-')