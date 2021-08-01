import json
import sys


def cmd(*args):
    """
    def.json [fname.html] - export glossary data
    """
    try:
        defs = args[0]
    except:
        raise SyntaxWarning()
    with open(defs, 'rt') as f:
        cfg = json.load(f)

    from ..glossary import Glossary

    g = Glossary(cfg)
    if len(args) > 1:
        out = open(args[1], 'wt')
    else:
        out = sys.stdout
    try:
        out.write(g.render())
    finally:
        if out != sys.stdout:
            out.close()
