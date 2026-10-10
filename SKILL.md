---
name: x-post-reader
description: Read and browse X/Twitter without login or an API key - read a post (including long-form X Articles), unroll threads, read replies and comments, list a user's timeline, followers and following, see trending topics, and search posts. Use when the user asks to read a tweet or post, look at someone's replies or recent posts, find posts on a topic, or browse X/Twitter, or when fetching x.com URLs returns an empty page, a login wall, or a "fetch failed" error.
---

# Read & Browse X/Twitter

## Overview

Never fetch `x.com` pages directly — they are a JavaScript shell that requires
login and returns nothing to a plain HTTP client. Use the free public mirror API
(FxEmbed / fxtwitter) instead. No key, no login, no proxy needed (the mirror
domains are not blocked in China). Rate limit is ~1000 req/min.

## When to use

- The user pastes an `x.com` / `twitter.com` link and asks what it says
- Reading the **comments / replies** under a post
- Unrolling a **thread**
- Looking at a **user's recent posts** (their timeline) or **followers/following**
- Seeing what's **trending**
- **Searching** for posts or people
- Batch-hydrating a list of URLs

Do NOT use for: posting/tweeting (read-only), or Bluesky (use api.fxbsky.app).

## Use the bundled script

The script wraps every endpoint and prints clean output (UTF-8, no JSON noise).

```bash
python scripts/xpost.py tweet https://x.com/user/status/1234567890
python scripts/xpost.py thread <url-or-id>
python scripts/xpost.py replies <url-or-id> --count 20    # the comment section
python scripts/xpost.py timeline <handle> --count 20
python scripts/xpost.py media <handle>
python scripts/xpost.py followers <handle> / following <handle>
python scripts/xpost.py user <handle>
python scripts/xpost.py trending --count 20
python scripts/xpost.py search "query" --count 20          # may return empty
python scripts/xpost.py search-users "query"
python scripts/xpost.py batch urls.txt
```

If you cannot run the script, replicate the endpoints below with your HTTP tool.

## Endpoints (all GET, base `https://api.fxtwitter.com/2`)

| Want | Endpoint |
|---|---|
| One post, full detail (incl. X Article body, media, views) | `https://api.fxtwitter.com/i/status/<id>` (v1) |
| Thread unrolled | `/2/thread/<id>` |
| Thread + **replies** | `/2/conversation/<id>` |
| User's posts (timeline) | `/2/profile/<handle>/statuses?count=N` |
| Posts with media | `/2/profile/<handle>/media` |
| Followers / following | `/2/profile/<handle>/followers` · `/following` |
| Profile | `/2/profile/<handle>` |
| Trending | `/2/trends?count=N` |
| Search posts / people | `/2/search?q=...` · `/2/search/users?q=...` |

Response shapes:
- single post: `{"status": {...}, "thread": [...]}`
- conversation: `{"status": {...}, "thread": [...], "replies": [...]}`
- lists: `{"results": [...], "cursor": {"bottom": "..."}}` — pass `cursor.bottom` to page.

## Common mistakes

- Fetching `x.com` directly → empty JS shell / `fetch failed`. Use the mirror API.
- `search` returns 404/empty for many queries — the free index is shallow. Do not
  treat empty as "nothing exists"; fall back to reading a specific post.
- On Windows, PowerShell `>` redirect re-encodes output to UTF-16; capture stdout
  directly, or pipe `| Out-File -Encoding utf8`.
- Reusing one HTTP connection behind a proxy can 401; open a fresh request per call.
- The v2 `status` object has no `views`/`media`/`article` — use the v1 `tweet` path
  (the script's `tweet` subcommand) when you need those.

## Rate limits

~1000 requests/minute per IP. Engagement counts are point-in-time snapshots.
