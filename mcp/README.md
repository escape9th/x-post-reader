# xpost MCP server

把「逛推特」做成 MCP server，Claude Desktop / Codex / Cursor 等任何 MCP 客户端都能直接当工具调用。

## 安装

```bash
pip install "mcp<2"          # FastMCP v1 接口；mcp v2 已把 FastMCP 改名，pin 到 <2 最省事
# 或 uv pip install "mcp<2"
```

## 配置

**Claude Desktop**（`claude_desktop_config.json`）：

```json
{
  "mcpServers": {
    "xpost": {
      "command": "python",
      "args": ["C:\\path\\to\\x-post-reader\\mcp\\server.py"]
    }
  }
}
```

**Codex**（`~/.codex/config.toml`）：

```toml
[mcp_servers.xpost]
command = "python"
args = ["C:\\path\\to\\x-post-reader\\mcp\\server.py"]
```

## 工具清单

| 工具 | 说明 |
|---|---|
| `get_tweet(url_or_id)` | 读一条（含长文全文、媒体、浏览数） |
| `get_replies(url_or_id, count)` | 看评论区 + thread |
| `get_thread(url_or_id)` | 展开 thread |
| `get_timeline(handle, count, include_replies)` | 用户最近推文 |
| `get_media(handle, count)` | 带图帖子 |
| `get_followers(handle, count)` / `get_following` | 粉丝 / 关注 |
| `get_user(handle)` | 用户资料 |
| `get_trending(count)` | 热门话题 |
| `search(query, count, feed)` | 搜帖子（浅索引，可能空） |
| `search_users(query, count)` | 搜人 |

全部只读、无 key、无登录。代理：自动读 `HTTP_PROXY`/`HTTPS_PROXY` 和 Windows 系统代理。
