# Usage

## Commands

| Command | What it does |
|---------|-------------|
| `mcpctl list` | Show all servers with type, scope, and description |
| `mcpctl list <server>` | Show server details: deps, notes, env vars, status |
| `mcpctl enable <server>` | Enable one or more servers |
| `mcpctl disable <server>` | Disable and auto-detect which scope to remove from |
| `mcpctl config` | Show config paths and defaults |

## Scopes

mcpctl writes to two locations:

- **Global** (`~/.claude.json`) - available in all projects
- **Project** (`.mcp.json`) - only in the current project

```bash
mcpctl enable --global memory        # all projects
mcpctl enable --project diagrams     # current project only
```

If you don't specify a scope, mcpctl prompts you and saves your choice as the default.

### Project root detection

`--project` finds your project root by walking up from the current directory looking for `.git`, `pyproject.toml`, `package.json`, `Cargo.toml`, `go.mod`, `pom.xml`, `Makefile`, or `Gemfile`. Falls back to the current directory if none found. No git repo required.

## Dry run

Preview what would change without writing anything:

```bash
mcpctl enable --dry-run diagrams
```

Shows a colored unified diff of the config changes.

## Dependencies

Servers can declare dependencies via the `deps` field. When enabling a server with deps, mcpctl asks you to confirm they're installed:

```
  'diagrams' needs graphviz. Installed? [y/N]:
```

Say yes to proceed, no to skip. mcpctl doesn't install anything for you.

## Environment variables

Servers that need API keys or credentials reference them with `${VAR}` in the YAML config. mcpctl resolves these from:

1. Shell environment variables
2. `~/.env` file
3. `.env` file in the current directory

Later sources override earlier ones.
