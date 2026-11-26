"""Block commits that contain private strings (LAN IPs, domains, names).

The patterns live OUTSIDE the repo, so the list itself never leaks:
~/.config/homelab/private-patterns.txt, one regex per line, # for comments.

LEARN [SEC]: gitleaks finds things that look like secrets (keys, tokens).
It can't know which strings are private *to you* (your real subnet, your
DuckDNS name, your employer). A personal denylist kept outside the repo
covers that gap.
"""

import re
import sys
from pathlib import Path

PATTERNS_FILE = Path.home() / ".config/homelab/private-patterns.txt"


def load_patterns(path: Path) -> list[re.Pattern[str]]:
    lines = path.read_text().splitlines()
    return [
        re.compile(line.strip(), re.IGNORECASE)
        for line in lines
        if line.strip() and not line.lstrip().startswith("#")
    ]


def find_matches(
    text: str, patterns: list[re.Pattern[str]]
) -> list[tuple[int, str]]:
    return [
        (lineno, p.pattern)
        for lineno, line in enumerate(text.splitlines(), 1)
        for p in patterns
        if p.search(line)
    ]


def main(files: list[str]) -> int:
    if not PATTERNS_FILE.exists():
        print(f"check_private: no {PATTERNS_FILE}, skipping (CI or new clone)")
        return 0
    patterns = load_patterns(PATTERNS_FILE)
    # Map each pattern to its line in the file, to report it by number
    lines = PATTERNS_FILE.read_text().splitlines()
    line_of = {line.strip(): n for n, line in enumerate(lines, 1)}
    print(f"check_private: {len(patterns)} patterns, {len(files)} files")
    failed = 0
    for name in files:
        text = Path(name).read_text(errors="ignore")
        for lineno, pattern in find_matches(text, patterns):
            # Print where the pattern lives, not the pattern or the line:
            # a literal pattern is the private value itself
            print(
                f"check_private: {name}:{lineno} matches pattern on line "
                f"{line_of[pattern]} of the patterns file"
            )
            failed = 1
    return failed


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
