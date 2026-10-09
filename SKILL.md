---
name: x-post-reader
description: Read X/Twitter posts and user profiles without login or an API key, including long-form posts (X Articles), and optionally search posts when an API key is available. Use when the user asks to read or look up a tweet or post, fetch an X/Twitter thread or profile, or search X/Twitter, or when fetching x.com URLs returns an empty page, a login wall, or a "fetch failed" error.
---

# Read X/Twitter Posts

## Overview

Never fetch `x.com` pages directly — they are a JavaScript shell that requires
login and returns nothing to a plain HTTP client. Read posts through public
JSON mirror APIs instead. No key, no login, no proxy needed (the mirror domains
are not blocked in China).

## When to use

- The user pastes an `x.com` / `twitter.com` link and asks what it says
- Reading many posts at once (batch-hydrate a list of URLs or ids)
- Looking up a user's profile (follower count, bio, join date)
- Fetching the full text of a long-form post (X Article)
- Keyword search — only when an API key is available (see below)

Do NOT use for: reading replies/comments (not available without login), or posting/tweeting.

## Quick reference — endpoints

| Want | Endpoint |
|---|---|
| Read a post (text + engagement + media) | `https://api.fxtwitter.com/<user>/status/<id>` |
| Read a post by id only | `https://api.fxtwitter.com/i/status/<id>` |
| Fallback | `https://api.vxtwitter.com/<user>/status/<id>` |
| Fallback (official) | `https://cdn.syndication.twimg.com/tweet-result?id=<id>&lang=en&token=a` |
| User profile | `https://api.fxtwitter.com/<user>` |

The fxtwitter response is JSON under a `tweet` key: `text`, `author`
(name / screen_name / followers), `created_at`, `likes`, `retweets`, `replies`,
`quotes`, `bookmarks`, `views`, `media`, and — for long-form posts —
`article.content.blocks[].text`.

## Use the bundled script

Prefer the script over hand-written code: it chains the three fallbacks, unwraps
the long-form article, and emits valid UTF-8.

```bash
python scripts/xpost.py tweet https://x.com/yaohui12138/status/2097151445883899913
python scripts/xpost.py tweet 2104912748794589515          # bare id also works
python scripts/xpost.py user xilo2991
python scripts/xpost.py batch urls.txt                     # one URL/id per line
python scripts/xpost.py search "AI agent" --bearer $TOKEN  # needs a key
```

If you cannot run the script, replicate the endpoint table with your own HTTP tool.

## Keyword search (optional, needs a key)

Free keyword search of X is NOT available without authentication (as of 2026).

1. **X API v2** — `GET https://api.x.com/2/tweets/search/recent?query=<q>&tweet.fields=created_at,public_metrics&user.fields=name,username&expansions=author_id` with `Authorization: Bearer <token>`. The script's `search` subcommand does this when given `--bearer` or `X_BEARER_TOKEN`.
2. **Third-party search APIs** (TwitterAPI.io, SocialData.tools, …) — each has its own key.
3. Search engines with `site:x.com` are unreliable — `cn.bing.com` ignores the operator, DuckDuckGo is blocked in China, and nitter mirrors are dead. Do not rely on them.

## Common mistakes

- Fetching `x.com` directly → empty JS shell / `fetch failed`. Use the mirror APIs.
- Expecting replies/comments → not available without login; report the `replies` count instead.
- On Windows, PowerShell `>` redirect re-encodes output to UTF-16; capture stdout directly, or use `--json`.
- Reusing one HTTP client/connection across requests behind a proxy can 401; open a fresh request per call.
- Assuming `site:x.com` search works → it does not on Chinese search engines.

## Rate limits

These mirror APIs are free but rate-limited. If fxtwitter returns 429/403, wait,
then fall back to vxtwitter, then the syndication endpoint. Engagement counts are
point-in-time snapshots.
