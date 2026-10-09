#!/usr/bin/env python3
"""xpost — read X/Twitter posts and profiles without an API key or login.

Uses the public mirror APIs (fxtwitter / vxtwitter) and Twitter's official
syndication endpoint. Standard library only — no pip install required.

Usage:
  python xpost.py tweet <url-or-id> [--json]
  python xpost.py user  <handle>
  python xpost.py batch <file-of-urls-or-ids>
  python xpost.py search <query> [--bearer TOKEN]     # needs an X API v2 bearer

Environment:
  HTTP_PROXY / HTTPS_PROXY   honoured automatically (also Windows system proxy).
  X_BEARER_TOKEN             used by `search` if --bearer is not given.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.parse
import urllib.request

# Always emit UTF-8, never crash on emoji / non-GBK characters. A GBK Windows
# console will show non-ASCII as mojibake, but redirected output (which is what
# an agent reads) stays valid UTF-8. Use --json for machine-readable output.
try:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")
except Exception:
    pass

UA = "curl/8.0"
TWEET_URL_RE = re.compile(
    r"(?:https?://)?(?:www\.|mobile\.)?(?:x|twitter)\.com/"
    r"([A-Za-z0-9_]{1,20})/status/(\d{10,25})", re.I)
BARE_ID_RE = re.compile(r"^\d{10,25}$")
HANDLE_RE = re.compile(r"^@?([A-Za-z0-9_]{1,20})$")

ENDPOINTS = {
    "fxtwitter": "https://api.fxtwitter.com",
    "vxtwitter": "https://api.vxtwitter.com",
    "syndication": "https://cdn.syndication.twimg.com/tweet-result",
}


def http_get(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": UA, "Accept": "*/*"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def parse_ref(value):
    """Return (handle, id) from a URL, a bare id, or '@handle'."""
    value = value.strip()
    m = TWEET_URL_RE.search(value)
    if m:
        return m.group(1), m.group(2)
    if BARE_ID_RE.match(value):
        return None, value
    m = HANDLE_RE.match(value)
    if m:
        return m.group(1), None
    return None, None


def _tweet_from_fxtwitter(handle, tid):
    url = f"{ENDPOINTS['fxtwitter']}/i/status/{tid}" if not handle \
        else f"{ENDPOINTS['fxtwitter']}/{handle}/status/{tid}"
    raw = http_get(url)
    d = json.loads(raw.decode("utf-8"))
    return d.get("tweet")


def _tweet_from_vxtwitter(handle, tid):
    url = f"{ENDPOINTS['vxtwitter']}/{handle}/status/{tid}" if handle \
        else f"{ENDPOINTS['vxtwitter']}/i/status/{tid}"
    raw = http_get(url)
    d = json.loads(raw.decode("utf-8"))
    return d.get("tweet")


def _tweet_from_syndication(tid):
    url = f"{ENDPOINTS['syndication']}?id={tid}&lang=en&token=a"
    raw = http_get(url)
    d = json.loads(raw.decode("utf-8"))
    return d


def fetch_tweet(ref):
    handle, tid = parse_ref(ref)
    if not tid:
        raise SystemExit(f"error: could not parse a tweet id from: {ref!r}")
    errors = []
    for name, fn in (
        ("fxtwitter", lambda: _tweet_from_fxtwitter(handle, tid)),
        ("vxtwitter", lambda: _tweet_from_vxtwitter(handle, tid)),
        ("syndication", lambda: _tweet_from_syndication(tid)),
    ):
        try:
            t = fn()
            if t:
                return name, t
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError) as e:
            errors.append(f"{name}: {e}")
    raise SystemExit("error: all tweet sources failed.\n  " + "\n  ".join(errors))


def fetch_user(handle):
    handle = handle.lstrip("@")
    for name, url in (
        ("fxtwitter", f"{ENDPOINTS['fxtwitter']}/{handle}"),
        ("vxtwitter", f"{ENDPOINTS['vxtwitter']}/{handle}"),
    ):
        try:
            raw = http_get(url)
            d = json.loads(raw.decode("utf-8"))
            u = d.get("user")
            if u:
                return name, u
        except (urllib.error.URLError, urllib.error.HTTPError, ValueError):
            continue
    raise SystemExit(f"error: could not resolve user @{handle}")


def _article_text(article):
    if not article:
        return ""
    blocks = (article.get("content") or {}).get("blocks") or []
    parts = [f"### {article.get('title', '')}"]
    for b in blocks:
        t = b.get("text") or ""
        parts.append(t)
    return "\n\n".join(parts)


def format_tweet(source, t):
    a = t.get("author") or {}
    lines = [
        f"### {a.get('name')} (@{a.get('screen_name')})",
        f"URL: {t.get('url')}  (source: {source})",
        f"created: {t.get('created_at')}",
        f"likes={t.get('likes')} retweets={t.get('retweets')} replies={t.get('replies')} "
        f"quotes={t.get('quotes')} bookmarks={t.get('bookmarks')} views={t.get('views')}",
        "",
        (t.get('text') or '').strip(),
    ]
    article = _article_text(t.get("article"))
    if article:
        lines += ["", "--- long-form post (X Article) ---", article]
    if t.get("quote"):
        q = t["quote"]
        qa = q.get("author") or {}
        lines += ["", f"> quoted @{qa.get('screen_name')}: {q.get('text')}"]
    media = t.get("media") or {}
    for key in ("videos", "photos"):
        for item in (media.get(key) or []):
            lines.append(f"media[{key}]: {item.get('url')}")
    return "\n".join(lines)


def cmd_tweet(args):
    source, t = fetch_tweet(args.ref)
    if args.json:
        print(json.dumps(t, ensure_ascii=False, indent=2))
    else:
        print(format_tweet(source, t))


def cmd_user(args):
    source, u = fetch_user(args.handle)
    print(json.dumps(u, ensure_ascii=False, indent=2))


def cmd_batch(args):
    refs = [ln.strip() for ln in open(args.file, encoding="utf-8") if ln.strip()]
    for i, ref in enumerate(refs):
        try:
            source, t = fetch_tweet(ref)
            print(format_tweet(source, t))
        except SystemExit as e:
            print(f"[{i}] {ref} -> {e}")
        print("\n" + "-" * 72 + "\n")


def cmd_search(args):
    token = args.bearer or os.environ.get("X_BEARER_TOKEN")
    if not token:
        raise SystemExit(
            "search needs an X API v2 bearer token.\n"
            "  - pass --bearer TOKEN, or set X_BEARER_TOKEN, or\n"
            "  - use a third-party search API (TwitterAPI.io, SocialData.tools, ...)\n"
            "Free keyword search of X is not available without a key (as of 2026).")
    q = urllib.parse.quote(args.query)
    url = ("https://api.x.com/2/tweets/search/recent?query=" + q +
           "&max_results=100&tweet.fields=created_at,public_metrics,author_id"
           "&user.fields=name,username,public_metrics&expansions=author_id")
    raw = http_get(urllib.request.Request(
        url, headers={"Authorization": f"Bearer {token}", "User-Agent": UA}))
    d = json.loads(raw.decode("utf-8"))
    users = {u["id"]: u for u in (d.get("includes") or {}).get("users", [])}
    for t in (d.get("data") or []):
        u = users.get(t.get("author_id"), {})
        m = t.get("public_metrics", {})
        print(f"@{u.get('username')}  {t.get('text')}  "
              f"[likes={m.get('like_count')} rt={m.get('retweet_count')}]")
    if "meta" in d:
        print(f"\n(next_token: {d['meta'].get('next_token')})")


def main(argv=None):
    p = argparse.ArgumentParser(prog="xpost", description=__doc__.splitlines()[0])
    sub = p.add_subparsers(dest="cmd", required=True)
    t = sub.add_parser("tweet", help="read one post by URL or id")
    t.add_argument("ref")
    t.add_argument("--json", action="store_true")
    t.set_defaults(fn=cmd_tweet)
    u = sub.add_parser("user", help="resolve a user profile")
    u.add_argument("handle")
    u.set_defaults(fn=cmd_user)
    b = sub.add_parser("batch", help="read many posts (one URL/id per line)")
    b.add_argument("file")
    b.set_defaults(fn=cmd_batch)
    s = sub.add_parser("search", help="keyword search (needs a bearer token)")
    s.add_argument("query")
    s.add_argument("--bearer")
    s.set_defaults(fn=cmd_search)
    args = p.parse_args(argv)
    args.fn(args)


if __name__ == "__main__":
    main()
