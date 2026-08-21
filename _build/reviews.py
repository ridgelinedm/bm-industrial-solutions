#!/usr/bin/env python3
"""Turn a Google Business Profile review export into _build/reviews.json.

    1. Drop the export into  _inbox/reviews/   (.json or .csv, any filename)
    2. python3 _build/reviews.py
    3. python3 _build/build.py

Handles the shapes these exports usually arrive in:

  * Google Takeout / Business Profile API JSON, where a rating reads
    "FIVE" and the reviewer sits under a nested "reviewer" object
  * A flat JSON array of review objects
  * CSV with any reasonable header naming (reviewer / name / author,
    rating / stars / score, comment / text / review, date / createTime)

Reviews with no written comment are skipped, since a star-only rating has
nothing to show on a card. Nothing here invents content: if the export is
missing or empty, reviews.json is written empty and the section on the site
simply does not render.
"""
import csv
import json
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
# Files may sit in _inbox/reviews/ or loose in _inbox/ as reviews*.json.
SRC_DIRS = [os.path.join(ROOT, "_inbox", "reviews"), os.path.join(ROOT, "_inbox")]
OUT = os.path.join(HERE, "reviews.json")

# Google reviews are public and carry full names. Flip this to True to render
# them as "Jane D." instead.
ABBREVIATE_SURNAMES = False

WORD_RATINGS = {"ONE": 1, "TWO": 2, "THREE": 3, "FOUR": 4, "FIVE": 5}

# "name" is last on purpose: in the Business Profile API export it holds the
# review's resource path, not the reviewer, so anything else must win first.
NAME_KEYS = ("reviewerdisplayname", "displayname", "reviewername", "author",
             "customer", "user", "name")
RATING_KEYS = ("starrating", "rating", "stars", "score", "rating_value")
TEXT_KEYS = ("comment", "text", "review", "reviewtext", "content", "body", "snippet")
DATE_KEYS = ("createtime", "date", "time", "published", "createdat", "review_date", "updatetime")

MONTHS = ["January", "February", "March", "April", "May", "June",
          "July", "August", "September", "October", "November", "December"]


def norm(k):
    return re.sub(r"[^a-z]", "", str(k).lower())


def pick(d, keys):
    lookup = {norm(k): v for k, v in d.items()}
    for k in keys:
        if k in lookup and lookup[k] not in (None, ""):
            return lookup[k]
    return None


def to_rating(v):
    if v is None:
        return None
    if isinstance(v, (int, float)):
        return int(round(float(v)))
    s = str(v).strip().upper()
    if s in WORD_RATINGS:
        return WORD_RATINGS[s]
    m = re.search(r"\d+(?:\.\d+)?", s)
    return int(round(float(m.group()))) if m else None


def to_date(v):
    """Return 'June 2025' style, or '' when the value is unusable."""
    if not v:
        return ""
    s = str(v).strip()
    m = re.match(r"(\d{4})-(\d{2})", s)
    if m:
        y, mo = int(m.group(1)), int(m.group(2))
        if 1 <= mo <= 12:
            return f"{MONTHS[mo - 1]} {y}"
    m = re.match(r"(\d{1,2})[/-](\d{1,2})[/-](\d{4})", s)
    if m:
        mo, y = int(m.group(1)), int(m.group(3))
        if 1 <= mo <= 12:
            return f"{MONTHS[mo - 1]} {y}"
    return ""


def clean_name(raw):
    if isinstance(raw, dict):
        raw = raw.get("displayName") or raw.get("name") or ""
    name = re.sub(r"\s+", " ", str(raw or "").strip())
    # Guard against picking up an API resource path by mistake.
    if "/" in name or name.startswith("accounts"):
        name = ""
    if not name:
        return "Google reviewer"
    if ABBREVIATE_SURNAMES:
        parts = name.split(" ")
        if len(parts) > 1:
            name = f"{parts[0]} {parts[-1][0]}."
    return name


def flatten(rec):
    """Pull the nested reviewer object up so pick() can see displayName."""
    out = dict(rec)
    reviewer = rec.get("reviewer")
    if isinstance(reviewer, dict):
        for k, v in reviewer.items():
            out.setdefault(f"reviewer{k}", v)
        out.setdefault("displayName", reviewer.get("displayName"))
    return out


def parse_record(rec):
    if not isinstance(rec, dict):
        return None
    rec = flatten(rec)
    text = pick(rec, TEXT_KEYS)
    if not text or not str(text).strip():
        return None  # star-only rating: nothing to put on a card
    rating = to_rating(pick(rec, RATING_KEYS))
    body = re.sub(r"\s+", " ", str(text).strip())
    # Some reviewers type their own star row. We render real stars, so drop it.
    body = re.sub(r"^[\s⭐★☆️\U0001F31F]+", "", body).strip()
    # Trailing rules some people sign off with ("————", "⸻") are decoration,
    # not content, so they are safe to trim. Punctuation *inside* a review is
    # left exactly as written: these are attributed quotes from real people.
    body = re.sub(r"\s*[–—⸺⸻]+\s*$", "", body)
    body = re.sub(r"\s*-{2,}\s*$", "", body).strip()
    return {
        "name": clean_name(pick(rec, NAME_KEYS)),
        "rating": rating if rating and 1 <= rating <= 5 else 5,
        "text": body,
        "date": to_date(pick(rec, DATE_KEYS)),
    }


def load_json(path):
    with open(path, encoding="utf-8-sig") as f:
        data = json.load(f)
    if isinstance(data, list):
        return data
    for key in ("reviews", "Reviews", "data", "items", "result"):
        if isinstance(data.get(key), list):
            return data[key]
    return [data]


def load_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        sample = f.read(4096)
        f.seek(0)
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
        except csv.Error:
            dialect = csv.excel
        return list(csv.DictReader(f, dialect=dialect))


def main():
    records = []
    seen_files = set()
    for src in SRC_DIRS:
        if not os.path.isdir(src):
            continue
        for fn in sorted(os.listdir(src)):
            path = os.path.join(src, fn)
            if not os.path.isfile(path) or fn.startswith("."):
                continue
            low = fn.lower()
            if not low.endswith((".json", ".csv", ".tsv")):
                continue
            # Loose files in _inbox/ must be named review*; the dedicated
            # reviews/ folder takes anything.
            if os.path.abspath(src) == os.path.abspath(SRC_DIRS[1]) and not low.startswith("review"):
                continue
            real = os.path.realpath(path)
            if real in seen_files:
                continue
            seen_files.add(real)
            try:
                records += load_json(path) if low.endswith(".json") else load_csv(path)
                print(f"  read {os.path.relpath(path, ROOT)}")
            except Exception as exc:
                print(f"  !! could not read {fn}: {exc}")
    if not seen_files:
        print("  no review export found in _inbox/reviews/ or _inbox/review*.json")

    parsed = [r for r in (parse_record(r) for r in records) if r]

    # De-duplicate on name + opening of the comment.
    seen, reviews = set(), []
    for r in parsed:
        key = (r["name"].lower(), r["text"][:60].lower())
        if key in seen:
            continue
        seen.add(key)
        reviews.append(r)

    # Longest first reads best in a masonry, and puts the substantial reviews
    # at the top of the first column.
    reviews.sort(key=lambda r: len(r["text"]), reverse=True)

    # Star-only ratings have no card to render but they still count toward the
    # rating shown on the Google profile, so track them separately.
    all_ratings = []
    for rec in records:
        if isinstance(rec, dict):
            r = to_rating(pick(flatten(rec), RATING_KEYS))
            if r and 1 <= r <= 5:
                all_ratings.append(r)

    payload = {
        "reviews": reviews,
        "count": len(reviews),                       # reviews with written text
        "total": len(all_ratings),                   # every rating on the profile
        "average": round(sum(all_ratings) / len(all_ratings), 1) if all_ratings else None,
    }
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)

    print(f"\n{len(records)} record(s) read, {len(reviews)} usable review(s) written to "
          f"{os.path.relpath(OUT, ROOT)}")
    if payload["average"]:
        print(f"average rating {payload['average']}")
    if not reviews:
        print("Nothing usable found, so the reviews section will not render.")
        if records:
            print("Records were read but had no comment text. Sample keys:",
                  sorted(records[0].keys())[:12] if isinstance(records[0], dict) else type(records[0]))
    return 0


if __name__ == "__main__":
    sys.exit(main())
