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
    #with open("x.html", "wt") as f:
    #    f.write(txt)

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
    g._sources[0].tags = "#x and #y"

