"""Tests for check_private.py. Run: uvx pytest scripts

TODO(you) [PY]: replace every `...` with real code. Each one is a single
expression; the comment above it tells you what goes there.
"""

import re

import check_private
import pytest


def test_load_patterns_skips_blanks_and_comments(tmp_path):
    # tmp_path is a pathlib.Path to an empty temp dir, fresh for each test.
    # `/` joins paths, like path.join(dir, "patterns.txt") in Node.
    patterns_file = tmp_path / "patterns.txt"

    # TODO(you) [PY]: one string with three lines: a pattern (e.g. secret),
    # an empty line, and a "# comment" line. Separate lines with "\n".
    patterns_file.write_text(r"192\.168\.1\.\d+" "\n\n# Test\n")

    patterns = check_private.load_patterns(patterns_file)
    # TODO(you) [PY]: how many patterns should survive the filter?
    assert len(patterns) == 1
    # A compiled regex keeps its source string in .pattern
    # TODO(you) [PY]: what string should that be?
    assert patterns[0].pattern == r"192\.168\.1\.\d+"


# parametrize runs the test once per tuple, passing the tuple's values as
# the arguments named in the first string ("text, expected").
# find_matches returns a list of (line_number, pattern_string) tuples.
@pytest.mark.parametrize(
    "text, expected",
    [
        ("nothing here", []),
        # TODO(you) [PY]: what comes back for an uppercase match on line 1?
        ("SECRET on line one", [(1, "secret")]),
        # TODO(you) [PY]: and for a match only on line 3?
        ("a\nb\nsecret", [(3, "secret")]),
    ],
)
def test_find_matches(text, expected):
    patterns = [re.compile("secret", re.IGNORECASE)]
    assert check_private.find_matches(text, patterns) == expected


def test_main_fails_without_echoing_the_value(tmp_path, monkeypatch, capsys):
    patterns_file = tmp_path / "patterns.txt"
    patterns_file.write_text("hunter2\n")
    leaky = tmp_path / "leaky.md"
    leaky.write_text("my value is hunter2\n")

    # monkeypatch.setattr(obj, "attr_name", new_value) replaces obj.attr_name
    # for this test only and restores it afterwards, even on failure.
    # TODO(you) [PY]: make check_private.PATTERNS_FILE point at patterns_file.
    monkeypatch.setattr(check_private, "PATTERNS_FILE", patterns_file)

    exit_code = check_private.main([str(leaky)])
    out = capsys.readouterr().out  # everything printed during the test

    # TODO(you) [PY]: what should main return when it finds a match?
    assert exit_code == 1
    # TODO(you) [PY] [SEC]: the private value must not be printed.
    assert "my value is" not in out
    assert "hunter2" not in out
