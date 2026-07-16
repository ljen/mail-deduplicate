from difflib import unified_diff
from unittest.mock import MagicMock

from mail_deduplicate.deduplicate import DuplicateSet
from mail_deduplicate.mail import DedupMailMixin


class MockConfig(dict):
    pass


def test_duplicate_set_diff():
    conf = MockConfig()
    mail_set = set()

    duplicateset = DuplicateSet("hash", mail_set, conf)

    mail_a = MagicMock(spec=DedupMailMixin)
    mail_a.body_lines = ["line 1\n", "line 2\n"]
    mail_a.timestamp = 1.0

    mail_b = MagicMock(spec=DedupMailMixin)
    mail_b.body_lines = ["line 1\n", "line 3\n"]
    mail_b.timestamp = 2.0

    diff_size = duplicateset.diff(mail_a, mail_b)

    expected_diff = "".join(
        unified_diff(
            mail_a.body_lines,
            mail_b.body_lines,
            fromfile="a",
            tofile="b",
            fromfiledate="",
            tofiledate="",
            n=0,
            lineterm="\n",
        )
    )
    assert diff_size == len(expected_diff)
    assert diff_size > 0


def test_duplicate_set_diff_same_body():
    conf = MockConfig()
    mail_set = set()

    duplicateset = DuplicateSet("hash", mail_set, conf)

    mail_a = MagicMock(spec=DedupMailMixin)
    mail_a.body_lines = ["line 1\n", "line 2\n"]
    mail_a.timestamp = 1.0

    mail_b = MagicMock(spec=DedupMailMixin)
    mail_b.body_lines = ["line 1\n", "line 2\n"]
    mail_b.timestamp = 2.0

    diff_size = duplicateset.diff(mail_a, mail_b)

    assert diff_size == 0
