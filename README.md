<p align="center">
  <img src="assets/hero.gif" alt="mcpctl - MCP server manager for Claude Code" width="800"/>
</p>

<p align="center">
  <a href="https://pypi.org/project/mcp-ctrl/"><img src="https://img.shields.io/pypi/v/mcp-ctrl.svg" alt="PyPI version"></a>
  <a href="https://www.python.org/downloads/"><img src="https://img.shields.io/badge/python-3.10+-blue.svg" alt="Python 3.10+"></a>
  <a href="https://opensource.org/licenses/MIT"><img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License: MIT"></a>
  <a href="https://modelcontextprotocol.io/"><img src="https://img.shields.io/badge/MCP-Compatible-green.svg" alt="MCP"></a>
  <br><br>
  Every MCP server you enable injects its tool definitions into your context window.<br>
  Enable 2-3 servers and you lose 100k+ tokens just on tool schemas.<br>
  <strong>mcpctl</strong> lets you toggle servers on and off with one command.
</p>

---

Works at both global (`~/.claude.json`) and project (`.mcp.json`) scope, handles container lifecycle for Docker/Podman servers, and substitutes environment variables for secrets.

> **⚠️ IMPORTANT DISCLAIMER**
>
> MCP servers can access your system resources, files, and network. **Different servers may behave differently and request varying levels of access to your machine.**
>
> **USE AT YOUR OWN RISK.** Always review server permissions, check the source repository, and only enable servers from trusted sources.

## ✨ Features

- 🚀 **Universal Management** - Single tool for all MCP server types (npm, python, docker)
- 🐳 **Container Runtime Auto-Detection** - Works with both Docker and Podman
- 📦 **Package Support** - npm (npx) and Python (uvx) packages
- 🔐 **Secrets Management** - Environment variable substitution from `.env` files
- ⚡ **Simple Commands** - list, config, enable, disable
- 📝 **YAML Configuration** - Human-readable server definitions
- 🔄 **Automatic Backups** - Claude config backed up before changes

## 📋 Table of Contents

- [Installation](#-installation)
- [Quick Start](#-quick-start)
- [Usage](#-usage)
- [Configuration](#-configuration)
- [Supported Server Types](#-supported-server-types)
- [Examples](#-examples)
- [Architecture](#-architecture)
- [Contributing](#-contributing)
- [License](#-license)

## 🚀 Installation

### Prerequisites

- Python 3.10 or higher
- Docker or Podman (for container-based MCP servers)
- Node.js (for npm-based MCP servers)
- Claude Code CLI

### Install with uv (recommended)

```bash
uv tool install mcp-ctrl
mcpctl list
```

### Install with pip

```bash
pip install mcp-ctrl
mcpctl list
```

### Install from source

```bash
git clone https://github.com/savitojs/mcpctl.git
cd mcpctl
uv sync
uv run mcpctl list
```

> **Note:** The PyPI package is named `mcp-ctrl`, but the command is `mcpctl`

> **Tip:** Managing Python environments? [setV](https://github.com/savitojs/setV) keeps them in one place with uv-backed creation, auto-freeze, and `setv doctor` to fix broken envs after OS upgrades.

## ⚡ Quick Start

### 1. Configure environment variables

mcpctl resolves `${VAR}` references from your shell environment first, then falls back to `.env` files. Set them wherever you prefer:

```bash
# Option A: shell profile (~/.zshenv, ~/.bashrc, ~/.profile, etc.)
export GITHUB_PAT=ghp_your_github_token_here
export EXA_API_KEY=your_exa_api_key

# Option B: dotenv file (~/.env)
GITHUB_PAT=ghp_your_github_token_here
EXA_API_KEY=your_exa_api_key
```

### 2. List available servers

```bash
mcpctl list
```

Output:
```
Available MCP Servers:

   ⚪ DISABLED   | filesystem              | npm        | Secure file operations
   ⚪ DISABLED   | github                  | npm        | GitHub repository management
   ⚪ DISABLED   | sequential-thinking     | npm        | Structured reasoning
🐳 ⚪ DISABLED   | postgres                | docker     | PostgreSQL database access
   ... (13 servers available in examples)
```

### 3. Enable a server

```bash
# Enable an npm-based server
mcpctl enable filesystem

# Enable a docker-based server (starts container automatically)
mcpctl enable postgres
```

### 4. Check details

```bash
mcpctl list filesystem
```

### 5. Disable when done

```bash
mcpctl disable filesystem
```

## 📖 Usage

### Commands

| Command | Description | Example |
|---------|-------------|---------|
| `list` | List all servers, or show details for one | `mcpctl list` / `mcpctl list github` |
| `config` | Show current configuration and paths | `mcpctl config` |
| `enable <server>` | Enable server(s), starts containers if needed | `mcpctl enable github filesystem` |
| `disable <server>` | Disable server(s) and stop containers | `mcpctl disable postgres` |

### Options

```bash
# Enable in global config (~/.claude.json)
mcpctl enable --global github

# Enable in project config (.mcp.json)
mcpctl enable --project github

# Preview changes without applying
mcpctl enable --dry-run github

# Disable server but keep container running
mcpctl disable postgres --keep-container

# Get help
mcpctl --help
mcpctl <command> --help
```

## ⚙️ Configuration

mcpctl stores configuration in `~/.config/mcpctl/`:
- `mcp-servers.yaml` - Your MCP server configurations

### Configuration File

`mcp-servers.yaml` defines all available MCP servers. See [examples/mcp-servers.example.yaml](examples/mcp-servers.example.yaml) for a complete example.

### Environment Variables

Use `${VAR_NAME}` syntax in YAML for environment variable substitution:

```yaml
env:
  GITHUB_TOKEN: "${GITHUB_TOKEN}"
```

Variables are resolved from (last wins):
1. `~/.env`
2. `.env` (project-local overrides)
3. Shell environment (`~/.zshenv`, `~/.bashrc`, `~/.profile`, etc.)

### Adding New MCP Servers

Edit `mcp-servers.yaml`:

```yaml
servers:
  my-server:
    type: npm  # or docker, python, executable
    description: "What this server does"
    transport: stdio
    requires_container: false
    mcp_config:
      command: npx
      args:
        - -y
        - "@org/my-mcp-server"
      env: {}
```

## 🎯 Supported Server Types

### 1. npm Package (npx)

```yaml
filesystem:
  type: npm
  requires_container: false
  mcp_config:
    command: npx
    args:
      - -y
      - "@modelcontextprotocol/server-filesystem"
      - /path/to/dir
```

### 2. Python Package (uvx)

```yaml
python-server:
  type: python
  requires_container: false
  mcp_config:
    command: uvx
    args:
      - python-mcp-package
```

### 3. Docker Container

```yaml
postgres:
  type: docker
  requires_container: true
  container:
    name: mcp-postgres
    image: postgres:16-alpine
    ports:
      - "5432:5432"
    environment:
      POSTGRES_PASSWORD: "${POSTGRES_PASSWORD}"
      POSTGRES_DB: mydb
  mcp_config:
    command: npx
    args:
      - -y
      - mcp-postgres
      - postgresql://postgres:${POSTGRES_PASSWORD}@localhost:5432/mydb
```

### 4. Custom Executable

```yaml
custom-server:
  type: executable
  requires_container: false
  mcp_config:
    command: /path/to/mcp-server
    args:
      - --config
      - /path/to/config.json
```

## 💡 Examples

### Enable PostgreSQL (with Docker container)

```bash
$ mcpctl enable postgres
ℹ️  Starting container: docker run -d --name mcp-postgres -p 5432:5432 ...
✅ Container 'mcp-postgres' started
✅ Server 'postgres' enabled in Claude config
⚠️  Restart Claude Code to apply changes
```

### Enable GitHub (npm package)

```bash
$ mcpctl enable github
✅ Server 'github' enabled in Claude config
⚠️  Restart Claude Code to apply changes
```

### Check Server Details

```bash
$ mcpctl list github

github
  Type:        remote
  Description: GitHub repository management (official remote server)
  Transport:   http
  Scope:       global
  Env vars:    GITHUB_PAT
```

### Show Configuration

```bash
$ mcpctl config

mcpctl configuration

  Config file:   ~/.config/mcpctl/mcp-servers.yaml
  Default scope: global
  Container:     /usr/bin/podman

Servers defined: 6
  filesystem
  github
  memory
  ...
```

## 🏗️ Architecture

```mermaid
flowchart TB
    subgraph mcpctl["mcpctl"]
        CLI["CLI (enable / disable / list / config)"]
    end

    YAML["~/.config/mcpctl/<br/>mcp-servers.yaml"]
    ENV["Environment<br/>shell env / .env files"]

    subgraph targets["Claude Config"]
        GLOBAL["~/.claude.json<br/>(global)"]
        PROJECT[".mcp.json<br/>(project)"]
    end

    subgraph containers["Container Runtime"]
        PODMAN["Podman / Docker"]
    end

    YAML -->|reads server<br/>definitions| CLI
    ENV -->|resolves<br/>${VAR} secrets| CLI
    CLI -->|writes mcpServers| GLOBAL
    CLI -->|writes mcpServers| PROJECT
    CLI -->|start / stop| PODMAN

    style mcpctl fill:#1e1b4b,stroke:#8b5cf6,color:#e2e8f0
    style CLI fill:#2e1065,stroke:#8b5cf6,color:#e2e8f0
    style YAML fill:#1e293b,stroke:#334155,color:#94a3b8
    style ENV fill:#1e293b,stroke:#334155,color:#94a3b8
    style GLOBAL fill:#14532d,stroke:#22c55e,color:#bbf7d0
    style PROJECT fill:#14532d,stroke:#22c55e,color:#bbf7d0
    style PODMAN fill:#172554,stroke:#3b82f6,color:#bfdbfe
    style targets fill:#0a1a0a,stroke:#22c55e,color:#86efac
    style containers fill:#0a1528,stroke:#3b82f6,color:#93c5fd
```

### How It Works

**Container servers (Docker/Podman):**
`enable` starts the container + writes to Claude config. `disable` stops it + removes the entry.

**Package servers (npm/Python):**
`enable` writes to Claude config (the package auto-runs when Claude needs it). `disable` removes the entry.

## 🛠️ Troubleshooting

### Container won't start

```bash
# Check Docker/Podman is running
docker ps  # or: podman ps

# Check container logs
docker logs <container-name>

# Manually start container
docker start <container-name>
# or with podman:
podman start <container-name>

# Then enable in Claude config
mcpctl enable <server-name>
```

### Environment variables not working

```bash
# Verify .env file
cat ~/.env

# Check substitution
mcpctl list github
```

### MCP not appearing in Claude Code

```bash
# Verify config added
cat ~/.claude.json | grep <server-name>

# Restart Claude Code
# (Exit and restart the CLI)
```

## 📚 Pre-Configured Servers

mcpctl includes example configurations for popular MCP servers. See the `~/.config/mcpctl/mcp-servers-examples.yaml` file or the `examples/` directory in the repository for 13+ pre-configured server examples including:

- File operations (filesystem)
- GitHub integration
- Browser automation (playwright, puppeteer)
- Database access (postgres)
- Web search (brave-search)
- Knowledge graphs (memory)
- HTTP requests (fetch)
- And more...

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Adding New Server Configurations

To contribute a new MCP server configuration:

1. Add server definition to `examples/mcp-servers.example.yaml`
2. Test with `mcpctl enable your-server`
3. Document any required environment variables
4. Submit PR with server details

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- [Model Context Protocol](https://modelcontextprotocol.io/) - The MCP specification
- [Claude Code](https://code.claude.com/) - AI-powered coding assistant
- [Anthropic](https://www.anthropic.com/) - Claude AI

## 📧 Support

- 📖 [Documentation](docs/)
- 🐛 [Issue Tracker](https://github.com/savitojs/mcpctl/issues)
- 💬 [Discussions](https://github.com/savitojs/mcpctl/discussions)

---

**Made with ❤️ for the Claude Code community**
