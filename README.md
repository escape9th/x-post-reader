# x-post-reader · 让 Agent 逛推特

**Read & browse X/Twitter — no API key, no login, no paid plan.**
A drop-in [Agent Skill](https://agentskills.io) + **MCP server** + CLI for
Claude Code, Codex, Cursor, and any MCP/agent client.

**无需 API key、无需登录、免费**地让 AI Agent 读取和浏览 X/Twitter（推特）：
读推文、看评论、翻时间线、查热门、搜帖子。

> 关键词 / Keywords：twitter api without key · read tweets without login ·
> x.com scraper · twitter scraping · twitter replies · tweet comments ·
> unroll twitter thread · twitter trending · free twitter search ·
> agent skill · claude code skill · codex skill · mcp server · mcp twitter

---

## 一句话 / TL;DR

抓 `x.com` 会拿到一个要登录的 JS 空壳。这个项目改走免费的公开镜像 API
（[FxEmbed / fxtwitter](https://docs.fxembed.com)），让 Agent 像逛网页一样逛推特。

## 能力 / What it can do（全部免费、无 key、无登录）

| 能力 Capability | 命令 Command |
|---|---|
| 读一条推文（含长文全文、媒体、浏览数）Read a post (full text, media, views, X Article) | `xpost.py tweet <url-or-id>` |
| 看评论区 / 回复 Read the **comments / replies** | `xpost.py replies <url-or-id>` |
| 展开 thread Unroll a thread | `xpost.py thread <url-or-id>` |
| 用户最近推文 A user's recent posts (timeline) | `xpost.py timeline <handle>` |
| 带图帖子 Posts with media | `xpost.py media <handle>` |
| 粉丝 / 关注 Followers / following | `xpost.py followers\|following <handle>` |
| 用户资料 Profile | `xpost.py user <handle>` |
| 热门话题 Trending topics | `xpost.py trending` |
| 搜帖子 / 搜人 Search posts / people | `xpost.py search\|search-users <query>` |
| 批量读链接 Batch-hydrate many URLs | `xpost.py batch urls.txt` |

## 实例 / Examples

**1. 读一条推文（带互动数据和完整正文）**

```bash
python scripts/xpost.py tweet https://x.com/yaohui12138/status/2097151445883899913
```

```
### 超级个体｜柿子 (@yaohui12138)
URL: https://x.com/yaohui12138/status/2097151445883899913  (source: fxtwitter)
created: Tue Sep 08 02:34:02 +0000 2026
likes=510 reposts=88 replies=133 quotes=14 bookmarks=837 views=46918

卧槽！我发现了一个能让普通人每月躺赚有机会10000刀的好生意！！
```

**2. 看评论区（之前要登录才拿得到，现在免费）**

```bash
python scripts/xpost.py replies 2104912748794589515 --count 5
```

```
--- replies (51) ---
@xilo2991 (2104956025766121621)  [likes=3, reposts=0, replies=1, Tue Sep 29 15:26]
    @FreeYoung552022 哇，这个不错啊，拿去国内做知识视频号就很ok了
@FreeYoung552022 (2104956679934919062)  [likes=1, reposts=0, Tue Sep 29 15:29]
    @xilo2991 是的，生成的很像某音精选的那种视频
```

**3. 翻某个账号的时间线**

```bash
python scripts/xpost.py timeline elonmusk --count 10
```

```
@elonmusk: 10 posts
@elonmusk (1234567890123456789)  [likes=45231, reposts=8901, replies=3210]
    Something about rockets and Mars ...
```

**4. 看现在什么在热**

```bash
python scripts/xpost.py trending --count 10
```

```
- #SmackDown  (Sports · Trending)
- KOLs  (Business & finance · Trending)
```

**5. 搜人 / 搜帖子**

```bash
python scripts/xpost.py search-users "OpenAI"
python scripts/xpost.py search "AI agent"
```

**6. 批量读一堆链接**（`urls.txt` 一行一个）

```bash
python scripts/xpost.py batch urls.txt
```

## 安装 / Install

零依赖，Python 3 标准库即可。代理自动读 `HTTP_PROXY`/`HTTPS_PROXY` 和 Windows 系统代理。

```bash
git clone https://github.com/escape9th/x-post-reader
```

**作为 Agent Skill（Claude Code / Codex / dsh）：**

```bash
# Claude Code
cp -r x-post-reader ~/.claude/skills/
# Codex
cp -r x-post-reader ~/.agents/skills/
# DeepSeek Harness (dsh)
cp -r x-post-reader ~/.agents/skills/
```

**作为 MCP server（Claude Desktop / Codex / Cursor）：**

```bash
pip install "mcp<2"
```

```json
{ "mcpServers": { "xpost": {
  "command": "python",
  "args": ["C:\\path\\to\\x-post-reader\\mcp\\server.py"]
} } }
```

MCP 工具清单（`get_tweet` / `get_replies` / `get_thread` / `get_timeline` /
`get_media` / `get_followers` / `get_following` / `get_user` / `get_trending` /
`search` / `search_users`）见 [mcp/README.md](mcp/README.md)。

## 原理 / How it works

1. 从 `x.com` / `twitter.com` 链接里解析出 handle + id（也接受裸 id）。
2. 走免费公开镜像 API：`api.fxtwitter.com/2/...`（浏览）+ v1（单条完整详情）。
3. 归一化成干净的 Markdown / JSON 输出。

**为什么别直接抓 `x.com`**：那个页面是 JS 空壳、要登录，普通 HTTP 客户端拿到的是
一堆脚本，正文一个字节都没有；在国内还连不上。

## 局限 / Limitations（实话）

- **只读** —— 不能发推、点赞、关注。
- **搜索是浅索引** —— 免费搜索接口经常返回空/404，别当完整索引；找具体内容用"读链接"最稳。
- 无 DM / 私密内容，只有公开内容。
- 镜像 API 免费但限流（约 1000 次/分钟）；互动数据是抓取时刻的快照。
- 还有别让大肥鱼看片

## License

MIT
