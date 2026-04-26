# Action Shorthand Reference (Claude.ai)

Canonical names and one-line summaries for every tool that commonly appears in a Claude.ai chat. Use these names verbatim in `→ Tools:` lines so logs are searchable and consistent across sessions.

## File and content tools

| Tool | When to log it | Example |
|---|---|---|
| `create_file` | Any new file Claude wrote to the workspace | `→ Tools: create_file` |
| `view` | Reading a file or directory | `→ Tools: view, web_search` |
| `str_replace` | Editing an existing file | `→ Tools: str_replace` |
| `present_files` | Delivering files to the user | `→ Tools: create_file, present_files` |
| `bash_tool` | Running shell commands | `→ Tools: bash_tool` |

## Visual / artifact tools

| Tool | When to log it | Example |
|---|---|---|
| `visualize:show_widget` | Inline SVG, HTML, charts, diagrams, mockups | `→ Tools: visualize:show_widget` |
| `image_search` | Inline image results in the chat | `→ Tools: image_search` |

If the artifact has a meaningful title, include it briefly on the Action line:
`→ Action: Built an interactive request-lifecycle diagram.`
`→ Tools: visualize:show_widget`

## Web tools

| Tool | When to log it | Example |
|---|---|---|
| `web_search` | Any web search call | `→ Tools: web_search` |
| `web_fetch` | Fetching a specific URL's contents | `→ Tools: web_fetch` |

If a search query is genuinely interesting (not just "stack overflow react hook"), include it in the Action line:
`→ Action: Searched for the latest Anthropic Claude Agent SDK auth flows.`
`→ Tools: web_search, web_fetch`

## Conversation memory tools

| Tool | When to log it | Example |
|---|---|---|
| `conversation_search` | Searching past chats by topic | `→ Tools: conversation_search` |
| `recent_chats` | Pulling chats by time window | `→ Tools: recent_chats` |
| `memory_user_edits` | Adding/changing memory facts | `→ Tools: memory_user_edits` |

## MCP server calls

Format: `mcp:{server-name}:{tool-name}`

| Example | Notes |
|---|---|
| `mcp:da-live:list_pages` | DA Live MCP page listing |
| `mcp:da-live:create_page` | DA Live MCP page creation |
| `mcp:google-drive:search` | Drive search |
| `mcp:google-drive:read_file` | Drive file fetch |

If multiple calls to the same MCP server happened in one turn, list it once. If you want a full count, include it briefly on the Action line: `Called the DA Live MCP 4 times to migrate the blog posts.`

## Other Claude.ai tools

| Tool | When to log it |
|---|---|
| `ask_user_input_v0` | When Claude asked the user multiple-choice questions |
| `places_search` / `places_map_display_v0` | Maps and locations |
| `weather_fetch` | Weather lookups |
| `recipe_display_v0` | Recipe widgets |
| `message_compose_v1` | Drafting emails / messages |
| `fetch_sports_data` | Sports scores/stats |
| `tool_search` / `search_mcp_registry` / `suggest_connectors` | Connector discovery |

## Status emoji on the Action line

Use one when the outcome is meaningful:

| Emoji | Meaning |
|---|---|
| ✅ | Complete and verified |
| ⚠️ | Partial or has caveats |
| ❌ | Blocked or failed |
| 🚧 | In progress, more work expected |
| 👀 | Awaiting user review |
| 📋 | Planning / scoping output |

## Examples of well-formed turns

**Simple Q&A turn (no tools):**
```markdown
→ Response: Explained the difference between OAuth authorization code flow and PKCE.
→ Action: Conceptual answer only, no artifacts.
→ Tools: none
```

**Web research turn:**
```markdown
→ Response: Confirmed the adaptTo() 2026 CFP closes May 15.
→ Action: Pulled dates and submission tracks from the conference site.
→ Tools: web_search, web_fetch
```

**Build turn:**
```markdown
→ Response: Drafted a React component for the priority queue dashboard.
→ Action: Rendered the artifact with mock data, three states (idle/running/blocked). ✅
→ Tools: visualize:show_widget
```

**MCP turn:**
```markdown
→ Response: Created two new EDS pages in the staging branch.
→ Action: Used the DA Live MCP to write the pages, verified via list call. ✅
→ Tools: mcp:da-live:create_page, mcp:da-live:list_pages
```

**Mixed turn:**
```markdown
→ Response: Diagnosed the Make.com webhook 502 as an upstream Playwright timeout.
→ Action: Pulled the failing run logs, proposed a retry-with-backoff config. 🚧
→ Tools: web_fetch, visualize:show_widget
```
