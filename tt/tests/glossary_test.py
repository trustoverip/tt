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
    s = Glossary(SAMPLE_GLOSSARY_CFG)
    txt = io.StringIO()
    s.write(txt)
    txt.seek(0)
    txt = txt.read()
    expected = ['<html>', '<head>', '</head>', '<body>',
                '<title>My Simple Glossary</title>',
                'wormhole',
                '<dt id="einstein-rosen-bridge">',
                'A speculative structure', '</dt>', '</dd>',
                '</dl>'
    ]
    missing = [x for x in expected if x not in txt]
    assert not bool(missing)


if __name__ == '__main__':
    test_ultra_simple_write()



