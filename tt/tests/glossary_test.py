import io
import json

from ..glossary import *

SAMPLE_GLOSSARY_CFG = json.loads("""{
    "title": "My Simple Glossary",
    "sources": [
        {
            "wiki": "git@github.com:dhh1128/scifi-terms.git"
        }
    ]
}""")


def test_ultra_simple_write():
    g = Glossary(SAMPLE_GLOSSARY_CFG)
    txt = g.render()

    expected = ['<html>', '<head>', '</head>', '<body>',
                '<title>My Simple Glossary</title>',
                'wormhole',
                '<dt id="einstein-rosen-bridge">',
                'A speculative structure', '</dt>', '</dd>',
                '</dl>'
    ]
    missing = [x for x in expected if x not in txt]
    assert not bool(missing)


def test_included_pages():
    g = Glossary(SAMPLE_GLOSSARY_CFG)
    x = g.render()
    # Filter out some of the terms
    g._sources[0].subset = tagsel.parse("#hardscience or #startrek")
    g._pages = None
    subset = g.render()
    assert len(x) > len(subset)


SAMPLE_GLOSSARY_SUBSET_CFG = json.loads("""{
    "title": "My Simple Glossary",
    "sources": [
        {
            "wiki": "git@github.com:dhh1128/scifi-terms.git",
            "subset": "not #startrek"
        }
    ]
}""")


def test_subset_in_config():
    g1 = Glossary(SAMPLE_GLOSSARY_CFG)
    x = g1.render()
    g2 = Glossary(SAMPLE_GLOSSARY_SUBSET_CFG)
    y = g2.render()
    assert len(x) > len(y)
