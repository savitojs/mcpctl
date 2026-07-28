# Installation

## Requirements

- Python 3.10+
- Claude Code installed

## Install from PyPI

```bash
pip install mcp-ctrl
```

The command is `mcpctl` (not `mcp-ctrl`).

## Install from source

```bash
git clone https://github.com/savitojs/mcpctl.git
cd mcpctl
pip install -e .
```

## Verify

```bash
mcpctl -v
mcpctl list
```

## First run

On first run, mcpctl creates `~/.config/mcpctl/` with an example config. Copy and edit it:

```bash
cp ~/.config/mcpctl/mcp-servers.yaml.example ~/.config/mcpctl/mcp-servers.yaml
$EDITOR ~/.config/mcpctl/mcp-servers.yaml
```

Remove servers you don't need, add environment variables for the ones you keep.
