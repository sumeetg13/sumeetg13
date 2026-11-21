#!/usr/bin/env python3
"""Adds a visitor's avatar to the petal wall in README.md.  Usage: petal.py <github-login>"""
import re
import sys
from pathlib import Path

START, END = "<!-- PETALS:START -->", "<!-- PETALS:END -->"
MAX_PETALS = 60


def main(login: str) -> None:
    if not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,38})", login):
        sys.exit(f"refusing unexpected login {login!r}")
    readme = Path(__file__).resolve().parent.parent / "README.md"
    text = readme.read_text()
    block = re.search(re.escape(START) + r"(.*?)" + re.escape(END), text, flags=re.S)
    existing = re.findall(r'href="https://github\.com/([A-Za-z0-9-]+)"', block.group(1))
    logins = [login] + [l for l in existing if l.lower() != login.lower()]
    cells = "\n".join(
        f'<a href="https://github.com/{l}" title="{l}"><img src="https://github.com/{l}.png?size=80" '
        f'width="40" height="40" alt="{l}"/></a>'
        for l in logins[:MAX_PETALS]
    )
    readme.write_text(text[:block.start()] + f"{START}\n{cells}\n{END}" + text[block.end():])


if __name__ == "__main__":
    main(sys.argv[1])
