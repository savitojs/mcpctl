# mcpctl

MCP server manager for Claude Code. Enable/disable MCP servers with container lifecycle.

## Rules

- Bump version in `mcpctl/__init__.py` and `pyproject.toml` on every change. Patch for fixes, minor for features.
- Commit after each logical change, not in batches.
- Single file CLI (`mcpctl/__main__.py`). Don't split into modules unless it passes 512 lines.
- Prefer podman over docker. Never hardcode `docker`.
- Atomic writes for config files (temp file, fsync, rename).
- `--dry-run` shows colored unified diff of what would change, writes nothing.
- All enable/disable operations are batch: one config read, one write, one diff.
- Backups go to `~/.claude-backups/` (last 5, dated). Never create backups in project directories.
- Deprecated npm packages removed: use `mcp-postgres` not `@modelcontextprotocol/server-postgres`, GitHub MCP is now a remote HTTP server at `api.githubcopilot.com/mcp`.
- Output style matches setV: `>>>` green prefix for success, `error:` red prefix, `warning:` yellow prefix.

## Project Info

- **Author**: Savitoj Singh <savv@duck.com>
- **PyPI package**: `mcp-ctrl` (command is `mcpctl`)
- **Python**: 3.10+
- **Dependencies**: pyyaml, rich
- **GitHub**: github.com/savitojs/mcpctl

## Testing

```bash
pip install -e .
mcpctl -v
mcpctl list
mcpctl enable --dry-run <server1> <server2>
mcpctl disable --dry-run <server1>
mcpctl config
```
