#!/usr/bin/env python3
"""Post-build sanity check: internal links, asset references and page metadata.

    python3 _build/check.py [--root dist] [--base ""]

Run it after `npm run build`; it reads the built site in dist/.

Exits non-zero if anything is broken, so it can gate a deploy.
"""
import argparse
import os
import re
import sys
from html.parser import HTMLParser

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT = os.path.join(REPO, "dist")  # replaced by --root in main()
SKIP_DIRS = {"_build", "_inbox", ".work", ".git", "assets", "node_modules"}


class Collector(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []      # (attr, value)
        self.imgs = []      # img tags, for alt checking
        self.title = None
        self._in_title = False
        self.h1_count = 0
        self.desc = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "a" and a.get("href"):
            self.refs.append(("href", a["href"]))
        elif tag in ("link",) and a.get("href"):
            self.refs.append(("href", a["href"]))
        elif tag in ("img", "script", "source"):
            for key in ("src", "srcset"):
                if a.get(key):
                    self.refs.append((key, a[key]))
            if tag == "img":
                self.imgs.append(a)
        elif tag == "title":
            self._in_title = True
        elif tag == "h1":
            self.h1_count += 1
        elif tag == "meta" and a.get("name") == "description":
            self.desc = a.get("content", "")

    def handle_endtag(self, tag):
        if tag == "title":
            self._in_title = False

    def handle_data(self, data):
        if self._in_title:
            self.title = (self.title or "") + data


def html_files():
    for dirpath, dirnames, filenames in os.walk(ROOT):
        dirnames[:] = [d for d in dirnames if d not in SKIP_DIRS and not d.startswith(".")]
        for fn in filenames:
            if fn.endswith(".html"):
                yield os.path.join(dirpath, fn)


def resolve(base, value):
    """Map a site-root URL to a path on disk. Returns None if not local."""
    if re.match(r"^(https?:|mailto:|tel:|#|data:)", value):
        return None
    if not value.startswith("/"):
        return None  # every internal link we emit is root-relative
    path = value.split("#")[0].split("?")[0]
    if base and path.startswith(base):
        path = path[len(base):]
    path = path.lstrip("/")
    disk = os.path.join(ROOT, path)
    if path == "" or path.endswith("/"):
        disk = os.path.join(disk, "index.html")
    return disk


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root", default="dist", help="Built site directory")
    ap.add_argument("--base", default="", help="Path prefix the site was built for")
    args = ap.parse_args()
    global ROOT
    ROOT = os.path.join(REPO, args.root)
    base = args.base.rstrip("/")

    problems = []
    pages = 0
    checked = 0

    for f in sorted(html_files()):
        rel = os.path.relpath(f, ROOT)
        pages += 1
        c = Collector()
        c.feed(open(f, encoding="utf-8").read())

        # Metadata hygiene
        if not c.title or len(c.title.strip()) < 10:
            problems.append(f"{rel}: missing or short <title>")
        elif len(c.title.strip()) > 75:
            problems.append(f"{rel}: title is {len(c.title.strip())} chars (>75 may truncate in search)")
        if not c.desc:
            problems.append(f"{rel}: missing meta description")
        elif not (60 <= len(c.desc) <= 175):
            problems.append(f"{rel}: meta description is {len(c.desc)} chars (aim 60-175)")
        if c.h1_count != 1:
            problems.append(f"{rel}: found {c.h1_count} <h1> elements (expected exactly 1)")

        for img in c.imgs:
            if "alt" not in img:
                problems.append(f"{rel}: <img> with no alt attribute ({img.get('src','?')})")

        # Link and asset targets
        for attr, value in c.refs:
            candidates = []
            if attr == "srcset":
                candidates = [p.strip().split(" ")[0] for p in value.split(",") if p.strip()]
            else:
                candidates = [value]
            for v in candidates:
                disk = resolve(base, v)
                if disk is None:
                    continue
                checked += 1
                if not os.path.exists(disk):
                    problems.append(f"{rel}: broken -> {v}")

    print(f"Scanned {pages} pages, {checked} internal references.")
    if problems:
        print(f"\n{len(problems)} problem(s):\n")
        for p in problems:
            print("  -", p)
        sys.exit(1)
    print("All internal links and assets resolve. Metadata looks sane.")


if __name__ == "__main__":
    main()
