import contextlib
import io
import pytest
import re

from .. import help

VALID_SYNTAX_DUMP_PAT = re.compile(r'\s*tt.*?https?://.*?[cC]ommand.*', re.S)


def test_syntax_works_without_args():
    with contextlib.redirect_stdout(io.StringIO()) as f:
        help.cmd()
        stdout = f.getvalue()
    assert VALID_SYNTAX_DUMP_PAT.match(stdout)


def test_syntax_works_with_many_args():
    with contextlib.redirect_stdout(io.StringIO()) as f:
        help.cmd(['a', 'b', 'c', 'd', 'e', 'f', 'g'])
        stdout = f.getvalue()
    assert VALID_SYNTAX_DUMP_PAT.match(stdout)
