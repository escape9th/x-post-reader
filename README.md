# x-post-reader

A drop-in agent skill for **reading X/Twitter posts** without an API key, login,
or paid plan — plus optional keyword search when you have a key.

> 一个给 Claude Code / Codex / DSH 等 agent 用的技能：**无 key、无登录读取 X/Twitter 推文**（含长文 X Article），可选关键词搜索。

## Why

Fetching `x.com` directly fails: the page is a JavaScript shell that needs login,
and a plain HTTP client gets nothing (or, in mainland China, the host is
unreachable). This skill routes around that with public JSON mirror APIs that
return the full post — text, author, engagement, media, and the complete body of
long-form posts (X Articles).

## What it can do

| Capability | Free | How |
|---|---|---|
| Read a post by URL or id | ✅ | `api.fxtwitter.com/<user>/status/<id>` |
| Full text of long-form posts | ✅ | included in the fxtwitter JSON |
| User profile | ✅ | `api.fxtwitter.com/<user>` |
| Batch-hydrate many URLs | ✅ | bundled script |
| Keyword search | 🔑 | needs an X API v2 bearer (or third-party) |
| Replies / comments | ❌ | not available without login |

## Install

Copy the repo into your agent's skills directory:

```bash
# Claude Code
cp -r x-post-reader ~/.claude/skills/

# Codex
cp -r x-post-reader ~/.agents/skills/

# DeepSeek Harness (dsh)
cp -r x-post-reader ~/.agents/skills/
```

Or install via your agent's skill-install command. The `SKILL.md` carries the
`name`/`description` frontmatter every agent reads when deciding what to load.

## Usage

```bash
python scripts/xpost.py tweet https://x.com/yaohui12138/status/2097151445883899913
python scripts/xpost.py tweet 2104912748794589515          # bare id works too
python scripts/xpost.py user xilo2991
python scripts/xpost.py batch urls.txt
python scripts/xpost.py search "AI agent" --bearer $X_BEARER_TOKEN
```

No dependencies — Python 3 standard library only. `HTTP_PROXY` / `HTTPS_PROXY`
(and the Windows system proxy) are honoured automatically.

## How it works

1. Parse the tweet handle + id out of any `x.com` / `twitter.com` URL (or accept
   a bare id).
2. Try the mirror APIs in order: fxtwitter → vxtwitter → Twitter's official
   syndication endpoint.
3. Normalise and print the result as Markdown, or `--json` for machine reading.

## Limitations (honest)

- **No replies/comments** — X requires login for those; this is not fixable
  from a public API.
- **No free keyword search** — X removed unauthenticated search; nitter is dead;
  Chinese search engines ignore `site:x.com`. Search needs a paid/authenticated
  key.
- Mirror APIs are free and rate-limited; engagement numbers are snapshots.

## License

MIT
