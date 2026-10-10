# x-post-reader

A drop-in agent skill that lets your agent **read and browse X/Twitter** — no API
key, no login, no paid plan.

> 让你的 Claude Code / Codex / dsh **逛推特**：读推文、看评论、翻时间线、查热门、搜帖子，全部免费、无需登录。

## What it can do (all free, no key)

| Capability | Command |
|---|---|
| Read a post (full detail, incl. long-form X Article) | `xpost.py tweet <url-or-id>` |
| Unroll a thread | `xpost.py thread <url-or-id>` |
| Read the **comments / replies** | `xpost.py replies <url-or-id>` |
| A user's recent posts (timeline) | `xpost.py timeline <handle>` |
| Posts with media | `xpost.py media <handle>` |
| Followers / following | `xpost.py followers\|following <handle>` |
| Profile | `xpost.py user <handle>` |
| Trending topics | `xpost.py trending` |
| Search posts / people | `xpost.py search\|search-users <query>` |
| Batch-hydrate many URLs | `xpost.py batch urls.txt` |

## How it works

The script hits the free **FxEmbed (fxtwitter)** API v2 (`https://api.fxtwitter.com/2`)
plus the v1 endpoint for full single-post detail (media, views, X Article body).
No dependencies — Python 3 standard library only. `HTTP_PROXY`/`HTTPS_PROXY` (and
the Windows system proxy) are honoured automatically.

## Install

```bash
# Claude Code
cp -r x-post-reader ~/.claude/skills/

# Codex
cp -r x-post-reader ~/.agents/skills/

# DeepSeek Harness (dsh)
cp -r x-post-reader ~/.agents/skills/
```

## MCP server

Also ships as an MCP server (`mcp/server.py`) so MCP clients call the same
capabilities as native tools instead of running a script. See
[mcp/README.md](mcp/README.md) for install and client config (Claude Desktop,
Codex, Cursor, …).

```bash
pip install "mcp<2"
```

## Limitations (honest)

- **Read-only** — can't post, like, follow.
- **Search is shallow** — the free search endpoint often returns empty/404; it's
  best-effort, not a complete index. For a specific post, always prefer reading by
  URL/id.
- **No DM / private content** — only public posts.
- Mirror APIs are free and rate-limited (~1000 req/min); counts are snapshots.

## License

MIT
