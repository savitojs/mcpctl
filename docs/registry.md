# Server Registry

mcpctl ships with a curated set of MCP servers in its example config. Here's what's available.

## Remote servers

No local install needed. Connect directly to hosted endpoints.

| Server | Description |
|--------|------------|
| `github` | GitHub issues, PRs, code search, and repo management |
| `context7` | Up-to-date, version-specific library docs to avoid hallucinated APIs |
| `deepwiki` | AI-powered docs and Q&A for any public GitHub repo, no auth needed |
| `supabase` | Manage Supabase projects, databases, auth, storage, and edge functions |
| `railway` | Deploy, manage, and monitor Railway projects and services |

## npm servers

Run via `npx`, no manual install needed.

| Server | Description |
|--------|------------|
| `filesystem` | Read, write, search, and manage files with configurable access paths |
| `sequential-thinking` | Step-by-step reasoning for complex problem decomposition |
| `memory` | Persistent memory across sessions using knowledge graphs |
| `playwright` | Browser automation, screenshots, and page inspection |
| `fetch` | HTTP GET/POST requests and URL content extraction |
| `chrome-devtools` | Inspect and control a running Chrome browser |
| `exa` | AI-native web search with semantic understanding |
| `sentry` | Query Sentry errors, issues, and performance data |
| `firecrawl` | Scrape, crawl, and search the web with structured data extraction |

## Python servers

Run via `uvx` or `python`. Some require `pip install` first.

| Server | Description |
|--------|------------|
| `time` | Current time and timezone conversion |
| `git` | Git log, diff, blame, branch, and commit operations |
| `notion` | Read and update Notion pages, databases, and blocks |
| `atlassian` | Search and update Jira issues and Confluence pages |
| `diagrams` | Render cloud architecture (AWS/GCP/K8s), Mermaid, and PlantUML diagrams |

## Docker servers

Require podman or docker. Container lifecycle managed by mcpctl.

| Server | Description |
|--------|------------|
| `excalidraw` | Interactive whiteboard diagrams with Excalidraw canvas |
| `postgres` | Run SQL queries and inspect PostgreSQL schema and data |
| `sonarqube` | Run SonarQube code quality and security scans |

## Adding your own

Edit `~/.config/mcpctl/mcp-servers.yaml` to add custom servers:

```yaml
servers:
  my-server:
    type: python
    description: "What it does"
    transport: stdio
    requires_container: false
    deps: []
    notes: []
    mcp_config:
      command: python
      args:
        - -m
        - my_mcp_server
      env: {}
```

Run `mcpctl list` to verify it appears, then `mcpctl enable my-server` to activate it.
