# 宣传文案包 / Launch Kit

> 每个渠道一套，复制粘贴即用。账号归你，文案归这里。

---

## X / Twitter（主战场，目标用户都在这）

**英文帖（主推）：**

> I made a free tool that lets your agent browse X/Twitter — no API key, no login.
>
> Read tweets, replies, threads, timelines, trending — even the full text of long-form X Articles. Ships as a Claude Code / Codex skill, an MCP server, and a Python CLI.
>
> 🧵 It works because it never scrapes x.com (that's a login-walled JS shell) — it uses the free public mirror API instead.
>
> GitHub: github.com/escape9th/x-post-reader

**中文帖：**

> 做了个免费工具，让 Claude Code / Codex 能逛推特：读推文、看评论、翻时间线、查热门，不用 API key、不用登录。
>
> 为什么之前别人做不了？因为直接抓 x.com 拿到的是要登录的 JS 空壳。这个走的是公开镜像 API。
>
> 支持三种形态：agent skill / MCP server / Python CLI。
>
> github.com/escape9th/x-post-reader

**可选 thread 第二、三条：**
- 「最大的坑不是技术，是所有人都去抓 x.com 页面，结果一个字都拿不到。」
- 「评论区（replies）这条之前只有登录才拿得到，现在免费就有了。」

---

## Hacker News（Show HN，dev 工具最合适）

**标题：** `Show HN: x-post-reader — browse X/Twitter without login or an API key`

**正文：**

> Agents can't read x.com: the page is a JavaScript shell that needs login, and the host is unreachable from some regions. I found the public mirror API (FxEmbed) exposes posts, replies, threads, timelines, followers, trending, and search as plain JSON, no key required.
>
> This repo packages that into three forms: a Claude Code / Codex skill (SKILL.md), an MCP server, and a stdlib-only Python CLI. Rate limit ~1000 req/min.
>
> Honest limitations: read-only, search is a shallow index (often empty), no DMs. Happy to answer questions.

---

## Reddit

**r/ClaudeAI / r/ClaudeCode：**

标题：`I made a Claude Code skill that lets your agent browse X/Twitter (no API key)`

正文：短段说明 + 链接 + 一句「feedback welcome」。⚠️ 注意每个 sub 的自荐比例规则（一般要 9:1，即 9 条正常参与 vs 1 条自荐），别一上来就只发自己的。

**r/mcp：**

标题：`[Server] x-post-reader — browse X/Twitter (replies, timelines, trending) via MCP`

正文：贴 MCP server 的配置片段 + 工具清单，问有没有想要的功能。

---

## Product Hunt

**Tagline：** Browse X/Twitter from your agent — no API key, no login

**描述：** Read posts, replies, threads, timelines, trending topics, and search X/Twitter from Claude Code, Codex, or any MCP client. Free, open source, stdlib-only Python.

**首条评论（自己发，抛问题）：** 「Built this after my agent kept getting blocked trying to read x.com links. What platform would you want next — Bluesky, Reddit, Telegram?」

---

## 中文社区

**即刻 / 掘金：**

> 让 AI Agent 逛推特：读推文、看评论、翻时间线、查热门，无需 API key、无需登录。
> 三种形态：Claude Code/Codex skill、MCP server、Python CLI。
> 核心原理一句话：不抓 x.com（登录墙），改走公开镜像 API。
> github.com/escape9th/x-post-reader

**V2EX（发在"分享创造"节点）：**

标题：`[分享创造] 让 Claude Code / Codex 能逛推特的开源工具（无 API key）`

**小红书（封面图 + 简短文案）：**

> AI Agent 现在能逛推特了👀
> 读推文 / 看评论 / 翻时间线，全免费不用 key
> 我还把它做成了 MCP server
> #AI工具 #Claude #程序员 #效率工具

---

## 发之前的三件事

1. **README 已经双语 + 带实例**，发帖时链接直接指向 `#examples` 那节。
2. **别同时在所有平台发一样的**，稍改语气；HN 偏"讲原理"，Reddit 偏"解决问题"，X 偏"一句话钩子"。
3. 把 GitHub topics（已加：`mcp` `agent-skill` `twitter` 等 17 个）当搜索引擎入口，等收录生效。
