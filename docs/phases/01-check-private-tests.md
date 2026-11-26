# 01: tests for check_private

- Plan phase: 1 (repo skeleton)
- Tags: PY, SEC

## Goal

Write the tests for the pre-commit hook that blocks private strings, and
learn pytest's three most-used features along the way.

## Files

- `scripts/test_check_private.py`: fill in the 9 `...` blanks
- `scripts/check_private.py`: the code under test (read it, don't change it)

## Concepts

- `tmp_path`: a fresh temporary directory per test, as a `pathlib.Path`.
- `@pytest.mark.parametrize`: one test, several input cases.
- `monkeypatch.setattr`: swap a module global for one test.
- `capsys`: capture what the code printed.
- Why the hook prints the pattern, not the matched line.

## Check

```sh
uvx pytest scripts
```

## Done when

All 5 tests pass, and the user can say in one sentence why the last
assert matters.
