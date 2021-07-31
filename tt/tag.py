import re

NON_ALPHANUMS_PAT = re.compile('[^a-z0-9]+', re.I)


def normalize(tag):
    """
    Return a canonical version of a tag. All non-alphanumeric chars are replaced with
    a single hyphen. Value is lower-case. Leading and trailing hyphens are trimmed.
    """
    return '#' + NON_ALPHANUMS_PAT.sub(' ', tag.lower()).strip().replace(' ', '-')


def edit_distance(tag1, tag2):
    tag1 = NON_ALPHANUMS_PAT.sub('', tag1.lower())
    tag2 = NON_ALPHANUMS_PAT.sub('', tag2.lower())
    return _damerau_levenshtein_distance(tag1, tag2)


def _damerau_levenshtein_distance(s1, s2):
    """
    Compute the Damerau-Levenshtein distance between two given
    strings (s1 and s2). Code from https://www.guyrutenberg.com/2008/12/15/damerau-levenshtein-distance-in-python/
    """
    d = {}
    lenstr1 = len(s1)
    lenstr2 = len(s2)
    for i in range(-1,lenstr1+1):
        d[(i,-1)] = i+1
    for j in range(-1,lenstr2+1):
        d[(-1,j)] = j+1

    for i in range(lenstr1):
        for j in range(lenstr2):
            if s1[i] == s2[j]:
                cost = 0
            else:
                cost = 1
            d[(i,j)] = min(
                           d[(i-1,j)] + 1, # deletion
                           d[(i,j-1)] + 1, # insertion
                           d[(i-1,j-1)] + cost, # substitution
                          )
            if i and j and s1[i]==s2[j-1] and s1[i-1] == s2[j]:
                d[(i,j)] = min (d[(i,j)], d[i-2,j-2] + cost) # transposition

    return d[lenstr1-1,lenstr2-1]