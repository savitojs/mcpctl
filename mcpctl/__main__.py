#!/usr/bin/env python3
"""
MCP Control - Universal MCP Server Manager
Manages MCP servers with different deployment types (npm, Docker, Python, etc.)
"""

import argparse
import difflib
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path
from typing import Dict, List, Optional

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip install pyyaml")
    sys.exit(1)

# Configuration paths
CONFIG_DIR = Path.home() / ".config" / "mcpctl"
CONFIG_FILE = CONFIG_DIR / "mcp-servers.yaml"
CLAUDE_GLOBAL_CONFIG = Path.home() / ".claude.json"

def detect_container_runtime() -> str | None:
    """Auto-detect podman or docker, return absolute path or None."""
    for cmd in ('podman', 'docker'):
        path = shutil.which(cmd)
        if path:
            return path
    return None


def require_container_runtime() -> str:
    """Return container runtime path or exit with error if none found."""
    runtime = detect_container_runtime()
    if not runtime:
        print_error("Neither podman nor docker found in PATH")
        sys.exit(1)
    return runtime

def find_project_root() -> Path | None:
    """Find project root via git, return None if not in a repo."""
    result = subprocess.run(
        ["git", "rev-parse", "--show-toplevel"],
        capture_output=True, text=True, check=False
    )
    if result.returncode == 0:
        return Path(result.stdout.strip())
    return None


def get_project_config_path() -> Path | None:
    """Return path to .mcp.json in the project root, or None."""
    root = find_project_root()
    if root:
        return root / ".mcp.json"
    return None


def get_saved_scope() -> str | None:
    """Read default scope from mcp-servers.yaml."""
    if not CONFIG_FILE.exists():
        return None
    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f) or {}
    return config.get('defaults', {}).get('scope')


def save_default_scope(scope: str) -> None:
    """Persist default scope to mcp-servers.yaml."""
    init_config_dir()
    with open(CONFIG_FILE) as f:
        config = yaml.safe_load(f) or {}
    if 'defaults' not in config:
        config['defaults'] = {}
    config['defaults']['scope'] = scope
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(config, f, default_flow_style=False, sort_keys=False)


def prompt_scope() -> str:
    """Ask user to pick global or project scope, save as default."""
    project_path = get_project_config_path()
    console.print(f"\n[bold]Where should MCP servers be configured?[/bold]\n")
    console.print(f"  1. Global  (~/.claude.json) - available in all projects")
    if project_path:
        console.print(f"  2. Project ({project_path.parent.name}/.mcp.json) - only this project")
    else:
        console.print(f"  2. Project (.mcp.json) - only this project (not in a git repo)")
    console.print()

    while True:
        choice = input("Choice [1/2]: ").strip()
        if choice == '1':
            scope = 'global'
            break
        elif choice == '2':
            if not project_path:
                print_error("Not in a git repository. Cannot use project scope.")
                continue
            scope = 'project'
            break

    save_as_default = input("Save as default? [Y/n]: ").strip().lower()
    if save_as_default in ('', 'y', 'yes'):
        save_default_scope(scope)
        print_success(f"Default scope set to '{scope}'")

    return scope


def resolve_target_config(scope_flag: str | None) -> Path:
    """Determine target config path from flag, saved default, or prompt."""
    if scope_flag == 'global':
        return CLAUDE_GLOBAL_CONFIG

    if scope_flag == 'project':
        project_path = get_project_config_path()
        if not project_path:
            print_error("Not in a git repository. Cannot use --project.")
            sys.exit(1)
        return project_path

    saved = get_saved_scope()
    if saved:
        if saved == 'project':
            project_path = get_project_config_path()
            if not project_path:
                print_warning("Default scope is 'project' but not in a git repo, using global")
                return CLAUDE_GLOBAL_CONFIG
            return project_path
        return CLAUDE_GLOBAL_CONFIG

    return prompt_scope_and_resolve()


def prompt_scope_and_resolve() -> Path:
    """Prompt for scope and return the target config path."""
    scope = prompt_scope()
    if scope == 'project':
        return get_project_config_path()
    return CLAUDE_GLOBAL_CONFIG


EXAMPLE_FILE = CONFIG_DIR / "mcp-servers.yaml.example"


def init_config_dir():
    """Initialize configuration directory with example file on first run."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    if CONFIG_FILE.exists():
        return

    _write_example_file()

    default_config = {'servers': {}}
    with open(CONFIG_FILE, 'w') as f:
        yaml.dump(default_config, f, default_flow_style=False, sort_keys=False)

    console.print(f"\n[blue]Created {CONFIG_FILE}[/blue]")
    console.print(f"[blue]Created {EXAMPLE_FILE}[/blue]")
    console.print(f"\n  To get started, copy the example and edit it:\n")
    console.print(f"    cp {EXAMPLE_FILE} {CONFIG_FILE}")
    console.print(f"    $EDITOR {CONFIG_FILE}")
    console.print(f"\n  Then remove servers you don't need and run:\n")
    console.print(f"    mcpctl list\n")


def _write_example_file():
    """Write bootstrap example file with popular MCP servers."""
    package_dir = Path(__file__).parent.parent
    bundled = package_dir / "examples" / "mcp-servers.example.yaml"
    if bundled.exists():
        shutil.copy(bundled, EXAMPLE_FILE)
        return

    EXAMPLE_FILE.write_text("""\
# mcpctl configuration
# Copy this file to mcp-servers.yaml and edit to your needs:
#   cp mcp-servers.yaml.example mcp-servers.yaml

# Environment variable sources (loaded in order, later wins)
env_files:
  - ~/.env
  - .env

# Default scope for enable command (global or project)
# Set automatically on first use, or edit here
# defaults:
#   scope: global

# MCP server definitions
servers:
  filesystem:
    type: npm
    description: Secure file operations with configurable access
    transport: stdio
    requires_container: false
    mcp_config:
      command: npx
      args: ["-y", "@modelcontextprotocol/server-filesystem", "/path/to/your/projects"]

  github:
    type: remote
    description: GitHub repository management (official remote server)
    transport: http
    requires_container: false
    mcp_config:
      type: http
      url: "https://api.githubcopilot.com/mcp"
      headers:
        Authorization: "Bearer ${GITHUB_PAT}"
    env_vars: [GITHUB_PAT]

  memory:
    type: npm
    description: Persistent memory using knowledge graphs
    transport: stdio
    requires_container: false
    mcp_config:
      command: npx
      args: ["-y", "@modelcontextprotocol/server-memory"]

  sequential-thinking:
    type: npm
    description: Structured reasoning and problem-solving
    transport: stdio
    requires_container: false
    mcp_config:
      command: npx
      args: ["-y", "@modelcontextprotocol/server-sequential-thinking"]

  context7:
    type: npm
    description: Version-pinned library docs in context
    transport: stdio
    requires_container: false
    mcp_config:
      command: npx
      args: ["-y", "@upstash/context7-mcp"]

  fetch:
    type: npm
    description: HTTP requests
    transport: stdio
    requires_container: false
    mcp_config:
      command: npx
      args: ["-y", "@kazuph/mcp-fetch"]
""")

from rich.console import Console

console = Console()
err_console = Console(stderr=True)


def _esc(msg: str) -> str:
    """Escape Rich markup characters in user-facing messages."""
    return msg.replace("[", "\\[")

def print_error(msg: str):
    err_console.print(f"[red]error:[/red] {_esc(msg)}")

def print_success(msg: str):
    console.print(f"[green]>>>[/green] {_esc(msg)}")

def print_warning(msg: str):
    console.print(f"[yellow]warning:[/yellow] {_esc(msg)}")

def print_info(msg: str):
    console.print(f"[blue]>>>[/blue] {_esc(msg)}")

def load_config() -> Dict:
    """Load MCP servers configuration from YAML"""
    # Initialize config directory if needed
    init_config_dir()

    if not CONFIG_FILE.exists():
        print_error(f"Configuration file not found: {CONFIG_FILE}")
        print_info("Run any mcpctl command to initialize default configuration")
        sys.exit(1)

    with open(CONFIG_FILE) as f:
        return yaml.safe_load(f)

def load_env_vars() -> Dict[str, str]:
    """Load environment variables from .env files"""
    env_vars = {}
    config = load_config()

    for env_file in config.get('env_files', []):
        env_path = Path(env_file).expanduser()
        if env_path.exists():
            with open(env_path) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key.strip()] = value.strip()

    # Add system environment variables
    env_vars.update(os.environ)
    return env_vars

def substitute_env_vars(text: str, env_vars: Dict[str, str]) -> str:
    """Replace ${VAR} with environment variable values"""
    import re

    def replacer(match):
        var_name = match.group(1)
        return env_vars.get(var_name, match.group(0))

    return re.sub(r'\$\{([^}]+)\}', replacer, text)

def get_server_config(server_name: str) -> Optional[Dict]:
    """Get configuration for a specific server"""
    config = load_config()
    return config.get('servers', {}).get(server_name)

def load_claude_config(target: Path = CLAUDE_GLOBAL_CONFIG) -> Dict:
    """Load Claude configuration from target path."""
    if not target.exists():
        return {"mcpServers": {}}

    with open(target) as f:
        return json.load(f)

def save_claude_config(config: Dict, target: Path = CLAUDE_GLOBAL_CONFIG):
    """Save Claude configuration atomically (write tmp, fsync, rename)."""
    import tempfile

    target.parent.mkdir(parents=True, exist_ok=True)

    if target.exists():
        from datetime import datetime
        stamp = datetime.now().strftime("%Y%m%d-%H%M%S")
        backup_dir = Path.home() / ".claude-backups"
        backup_dir.mkdir(exist_ok=True)
        if target.name == ".mcp.json":
            prefix = f"{target.parent.name}.mcp.json"
        else:
            prefix = target.name
        shutil.copy2(str(target), str(backup_dir / f"{prefix}.{stamp}"))
        backups = sorted(backup_dir.glob(f"{prefix}.*"))
        for old in backups[:-5]:
            old.unlink()

    tmp_fd, tmp_path = tempfile.mkstemp(
        dir=target.parent, suffix=".tmp", prefix=".claude-"
    )
    try:
        with os.fdopen(tmp_fd, "w") as f:
            json.dump(config, f, indent=2)
            f.write("\n")
            f.flush()
            os.fsync(f.fileno())
        os.replace(tmp_path, str(target))
    except BaseException:
        os.unlink(tmp_path)
        raise

def run_command(cmd: List[str], check: bool = True, capture: bool = False) -> subprocess.CompletedProcess:
    """Run shell command"""
    if capture:
        return subprocess.run(cmd, capture_output=True, text=True, check=check)
    return subprocess.run(cmd, check=check)

def is_container_running(container_name: str) -> bool:
    """Check if Docker/Podman container is running"""
    runtime = require_container_runtime()
    result = run_command(
        [runtime, "ps", "--format", "{{.Names}}", "--filter", f"name=^{container_name}$"],
        check=False,
        capture=True
    )
    return container_name in result.stdout

def start_container(server_name: str, server_config: Dict) -> bool:
    """Start Docker/Podman container for MCP server"""
    if not server_config.get('requires_container'):
        print_warning(f"Server '{server_name}' does not require a container")
        return True

    container = server_config.get('container', {})
    if not container:
        print_error(f"No container configuration found for '{server_name}'")
        return False

    container_name = container['name']

    # Check if already running
    if is_container_running(container_name):
        print_warning(f"Container '{container_name}' already running")
        return True

    runtime = require_container_runtime()

    # Remove if exists but stopped
    run_command([runtime, "ps", "-a", "--filter", f"name=^{container_name}$", "--format", "{{.Names}}"],
                check=False, capture=True)
    run_command([runtime, "rm", "-f", container_name], check=False, capture=False)

    # Build container run command
    cmd = [runtime, "run", "-d", "--name", container_name]

    # Add ports
    for port_mapping in container.get('ports', []):
        cmd.extend(["-p", port_mapping])

    # Add environment variables
    env_vars = load_env_vars()
    for key, value in container.get('environment', {}).items():
        value = substitute_env_vars(value, env_vars)
        cmd.extend(["-e", f"{key}={value}"])

    # Add image
    cmd.append(container['image'])

    print_info(f"Starting container: {' '.join(cmd)}")
    result = run_command(cmd, check=False)

    if result.returncode == 0:
        print_success(f"Container '{container_name}' started")
        return True
    else:
        print_error(f"Failed to start container '{container_name}'")
        return False

def stop_container(server_name: str, server_config: Dict) -> bool:
    """Stop Docker/Podman container"""
    if not server_config.get('requires_container'):
        print_warning(f"Server '{server_name}' does not have a container")
        return True

    container = server_config.get('container', {})
    container_name = container.get('name')

    if not is_container_running(container_name):
        print_warning(f"Container '{container_name}' not running")
        return True

    runtime = require_container_runtime()
    result = run_command([runtime, "stop", container_name], check=False)
    run_command([runtime, "rm", container_name], check=False)

    if result.returncode == 0:
        print_success(f"Container '{container_name}' stopped")
        return True
    else:
        print_error(f"Failed to stop container '{container_name}'")
        return False

def show_config_diff(before: Dict, after: Dict, target: Path = CLAUDE_GLOBAL_CONFIG) -> None:
    """Print colored unified diff of claude config changes."""
    path = str(target)
    old = json.dumps(before, indent=2).splitlines(keepends=True)
    new = json.dumps(after, indent=2).splitlines(keepends=True)
    diff = list(difflib.unified_diff(old, new, fromfile=path, tofile=path))
    if not diff:
        print_warning("No changes")
        return
    for line in diff:
        line = line.rstrip('\n')
        escaped = line.replace('[', '\\[')
        if line.startswith('+++') or line.startswith('---'):
            console.print(f"[blue]{escaped}[/blue]")
        elif line.startswith('+'):
            console.print(f"[green]{escaped}[/green]")
        elif line.startswith('-'):
            console.print(f"[red]{escaped}[/red]")
        elif line.startswith('@@'):
            console.print(f"[yellow]{escaped}[/yellow]")
        else:
            console.print(escaped)


def prepare_mcp_config(server_config: Dict) -> Dict:
    """Build resolved mcp_config for a server (env vars, absolute paths)."""
    mcp_config = server_config['mcp_config'].copy()
    env_vars = load_env_vars()

    if server_config.get('type') == 'remote':
        return mcp_config

    is_docker = mcp_config.get('command') == 'docker'

    if is_docker:
        mcp_config['command'] = require_container_runtime()
    else:
        resolved = shutil.which(mcp_config['command'])
        if resolved:
            mcp_config['command'] = resolved

    if 'args' in mcp_config:
        if is_docker:
            resolved_env = {
                k: substitute_env_vars(v, env_vars)
                for k, v in mcp_config.get('env', {}).items()
            }
            new_args = []
            skip_next = False
            for i, arg in enumerate(mcp_config['args']):
                if skip_next:
                    skip_next = False
                    continue
                if arg == '-e' and i + 1 < len(mcp_config['args']):
                    next_arg = mcp_config['args'][i + 1]
                    if '=' not in next_arg and next_arg in resolved_env:
                        new_args.append('-e')
                        new_args.append(f"{next_arg}={resolved_env[next_arg]}")
                        skip_next = True
                    else:
                        new_args.append(arg)
                else:
                    new_args.append(substitute_env_vars(str(arg), env_vars))
            mcp_config['args'] = new_args
        else:
            mcp_config['args'] = [
                substitute_env_vars(str(arg), env_vars) for arg in mcp_config['args']
            ]

    if is_docker:
        mcp_config.pop('env', None)
    elif 'env' in mcp_config:
        mcp_config['env'] = {
            k: substitute_env_vars(v, env_vars)
            for k, v in mcp_config['env'].items()
        }

    return mcp_config


def enable_servers(server_names: List[str], dry_run: bool = False,
                   target: Path = CLAUDE_GLOBAL_CONFIG) -> bool:
    """Enable one or more MCP servers in a single config write."""
    claude_config = load_claude_config(target)
    before = json.loads(json.dumps(claude_config))
    if 'mcpServers' not in claude_config:
        claude_config['mcpServers'] = {}

    failed = []
    enabled = []
    for name in server_names:
        server_config = get_server_config(name)
        if not server_config:
            print_error(f"Server '{name}' not found in configuration")
            failed.append(name)
            continue

        if not dry_run and server_config.get('requires_container'):
            if not start_container(name, server_config):
                failed.append(name)
                continue

        claude_config['mcpServers'][name] = prepare_mcp_config(server_config)
        enabled.append(name)

    if not enabled:
        return len(failed) == 0

    if dry_run:
        show_config_diff(before, claude_config, target)
        return len(failed) == 0

    save_claude_config(claude_config, target)
    scope_label = "project" if target.name == ".mcp.json" else "global"
    print_success(f"Enabled ({scope_label}): {', '.join(enabled)}")
    print_warning("Restart Claude Code to apply changes")
    return len(failed) == 0


def find_server_scope(name: str) -> List[Path]:
    """Return list of config files where this server is currently enabled."""
    found = []
    global_config = load_claude_config(CLAUDE_GLOBAL_CONFIG)
    if name in global_config.get('mcpServers', {}):
        found.append(CLAUDE_GLOBAL_CONFIG)

    project_path = get_project_config_path()
    if project_path:
        project_config = load_claude_config(project_path)
        if name in project_config.get('mcpServers', {}):
            found.append(project_path)

    return found


def _prompt_dual_scope() -> str:
    """Ask once which scope to remove from when servers are in both."""
    console.print(f"  1. Global  (~/.claude.json)")
    console.print(f"  2. Project (.mcp.json)")
    console.print(f"  3. Both")
    while True:
        choice = input("Remove from [1/2/3]: ").strip()
        if choice in ('1', '2', '3'):
            return choice


def disable_servers(server_names: List[str], stop_container_flag: bool = True,
                    dry_run: bool = False, scope_flag: str | None = None) -> bool:
    """Disable servers, auto-detecting which config file they live in."""
    scopes: dict[str, list[Path]] = {}
    for name in server_names:
        if scope_flag:
            scopes[name] = [resolve_target_config(scope_flag)]
        else:
            scopes[name] = find_server_scope(name)

    dual_scope_servers = [n for n, t in scopes.items() if len(t) > 1]
    dual_choice = None
    if dual_scope_servers:
        print_warning(f"These servers are enabled in both global and project: {', '.join(dual_scope_servers)}")
        dual_choice = _prompt_dual_scope()

    changes: dict[Path, list[str]] = {}
    for name in server_names:
        targets = scopes[name]

        if not targets:
            print_warning(f"Server '{name}' not enabled anywhere, nothing to disable")
            continue

        if len(targets) > 1 and dual_choice:
            if dual_choice == '1':
                targets = [CLAUDE_GLOBAL_CONFIG]
            elif dual_choice == '2':
                targets = [t for t in targets if t.name == '.mcp.json']

        for t in targets:
            changes.setdefault(t, []).append(name)

    if not changes:
        return True

    for target, names in changes.items():
        config = load_claude_config(target)
        before = json.loads(json.dumps(config))
        for name in names:
            if name in config.get('mcpServers', {}):
                del config['mcpServers'][name]

        scope_label = "project" if target.name == ".mcp.json" else "global"

        if dry_run:
            show_config_diff(before, config, target)
            continue

        save_claude_config(config, target)
        print_success(f"Disabled ({scope_label}): {', '.join(names)}")

        if stop_container_flag:
            for name in names:
                server_config = get_server_config(name)
                if server_config and server_config.get('requires_container'):
                    stop_container(name, server_config)

    if not dry_run:
        print_warning("Restart Claude Code to apply changes")
    return True

def list_servers(server_name: str | None = None):
    """List servers in a table, or show details for a specific server."""
    from rich.table import Table
    config = load_config()
    global_config = load_claude_config(CLAUDE_GLOBAL_CONFIG)
    global_servers = set(global_config.get('mcpServers', {}).keys())

    project_path = get_project_config_path()
    project_servers = set()
    if project_path:
        project_config = load_claude_config(project_path)
        project_servers = set(project_config.get('mcpServers', {}).keys())

    if server_name:
        _show_server_detail(console, server_name, config, global_servers, project_servers)
        return

    table = Table(title="MCP Servers", show_lines=False, pad_edge=False)
    table.add_column("Server", style="bold")
    table.add_column("Type", style="dim")
    table.add_column("Scope", justify="center")
    table.add_column("Description")

    for name, server_config in config.get('servers', {}).items():
        in_global = name in global_servers
        in_project = name in project_servers

        if in_global and in_project:
            scope = "[green]G[/green]+[cyan]P[/cyan]"
        elif in_global:
            scope = "[green]G[/green]"
        elif in_project:
            scope = "[cyan]P[/cyan]"
        else:
            scope = "[dim]-[/dim]"

        server_type = server_config.get('type', 'unknown')
        desc = server_config.get('description', '')

        if in_global or in_project:
            name_cell = f"[green]{name}[/green]"
        else:
            name_cell = f"[dim]{name}[/dim]"
        table.add_row(name_cell, server_type, scope, desc)

    console.print()
    console.print(table)
    console.print("\n  [dim]G = Global (~/.claude.json)  P = Project (.mcp.json)[/dim]")
    console.print(f"  [dim]mcpctl list <server> for details[/dim]\n")


def _show_server_detail(console, name: str, config: Dict,
                        global_servers: set, project_servers: set):
    """Show detailed info for a single server."""
    server_config = config.get('servers', {}).get(name)
    if not server_config:
        print_error(f"Server '{name}' not found in configuration")
        return

    console.print(f"\n[bold]{name}[/bold]")
    console.print(f"  Type:        {server_config.get('type', 'unknown')}")
    console.print(f"  Description: {server_config.get('description', '')}")
    console.print(f"  Transport:   {server_config.get('transport', 'stdio')}")

    in_global = name in global_servers
    in_project = name in project_servers
    if in_global and in_project:
        console.print(f"  Scope:       [green]global[/green] + [cyan]project[/cyan]")
    elif in_global:
        console.print(f"  Scope:       [green]global[/green]")
    elif in_project:
        console.print(f"  Scope:       [cyan]project[/cyan]")
    else:
        console.print(f"  Scope:       [dim]not enabled[/dim]")

    mcp_config = server_config.get('mcp_config', {})
    console.print(f"  Command:     {mcp_config.get('command', '')}")
    if mcp_config.get('args'):
        console.print(f"  Args:        {' '.join(str(a) for a in mcp_config['args'])}")

    env_vars = server_config.get('env_vars', [])
    if env_vars:
        console.print(f"  Env vars:    {', '.join(env_vars)}")

    if server_config.get('requires_container'):
        container = server_config.get('container', {})
        container_name = container.get('name', '')
        console.print(f"  Container:   {container_name}")
        runtime = detect_container_runtime()
        if runtime:
            running = is_container_running(container_name)
            status = "[green]running[/green]" if running else "[yellow]stopped[/yellow]"
            console.print(f"  Status:      {status}")
        else:
            console.print(f"  Status:      [dim]no container runtime[/dim]")

    console.print()

def show_config():
    """Show current mcpctl configuration."""
    config = load_config()

    console.print(f"\n[bold]mcpctl configuration[/bold]\n")
    console.print(f"  Config file:   {CONFIG_FILE}")
    console.print(f"  Example file:  {EXAMPLE_FILE}")

    saved_scope = get_saved_scope()
    console.print(f"  Default scope: {saved_scope or '[dim]not set (will prompt)[/dim]'}")

    runtime = detect_container_runtime()
    console.print(f"  Container:     {runtime or '[dim]not found[/dim]'}")

    project_path = get_project_config_path()
    if project_path:
        console.print(f"  Project config: {project_path}")

    env_files = config.get('env_files', [])
    if env_files:
        console.print(f"\n[bold]Environment files:[/bold]")
        for ef in env_files:
            path = Path(ef).expanduser()
            status = "[green]found[/green]" if path.exists() else "[dim]not found[/dim]"
            console.print(f"  {ef} ({status})")

    servers = config.get('servers', {})
    console.print(f"\n[bold]Servers defined:[/bold] {len(servers)}")
    for name in servers:
        console.print(f"  {name}")
    console.print()


def main():
    parser = argparse.ArgumentParser(
        prog="mcpctl",
        description="Manage MCP servers for Claude Code.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""examples:
  mcpctl list                           Show all servers and where they're enabled
  mcpctl enable memory filesystem       Enable servers (prompts for scope on first use)
  mcpctl enable --global memory         Enable in ~/.claude.json (all projects)
  mcpctl enable --project memory        Enable in .mcp.json (this project only)
  mcpctl enable --dry-run memory        Preview what would change
  mcpctl disable memory                 Auto-detects scope, removes from where it's enabled
  mcpctl list memory                    Show server details and container status
  mcpctl config                         Show configuration and paths

config:
  Server definitions:  ~/.config/mcpctl/mcp-servers.yaml
  Example file:        ~/.config/mcpctl/mcp-servers.yaml.example
  Backups:             ~/.claude-backups/ (last 5, by date)
  Env vars:            shell env (~/.zshenv, ~/.bashrc, etc.) or .env files
        """
    )

    from mcpctl import __version__
    parser.add_argument('-v', '--version', action='version', version=f'mcpctl {__version__}')

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # list command
    list_parser = subparsers.add_parser('list', help='List servers, or show details for one')
    list_parser.add_argument('server', nargs='?', help='Server name for details')

    # config command
    subparsers.add_parser('config', help='Show current configuration')

    # enable command
    enable_parser = subparsers.add_parser('enable', help='Enable MCP server(s)')
    enable_parser.add_argument('servers', nargs='+', help='Server name(s)')
    enable_parser.add_argument('--dry-run', action='store_true',
                               help='Preview changes without applying')
    enable_scope = enable_parser.add_mutually_exclusive_group()
    enable_scope.add_argument('--global', dest='scope', action='store_const',
                              const='global', help='Enable in ~/.claude.json')
    enable_scope.add_argument('--project', dest='scope', action='store_const',
                              const='project', help='Enable in .mcp.json')

    # disable command
    disable_parser = subparsers.add_parser('disable', help='Disable MCP server(s)')
    disable_parser.add_argument('servers', nargs='+', help='Server name(s)')
    disable_parser.add_argument('--keep-container', action='store_true',
                               help='Keep container running')
    disable_parser.add_argument('--dry-run', action='store_true',
                                help='Preview changes without applying')
    disable_scope = disable_parser.add_mutually_exclusive_group()
    disable_scope.add_argument('--global', dest='scope', action='store_const',
                               const='global', help='Disable in ~/.claude.json')
    disable_scope.add_argument('--project', dest='scope', action='store_const',
                               const='project', help='Disable in .mcp.json')

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        sys.exit(1)

    # Execute command
    try:
        if args.command == 'list':
            list_servers(args.server)

        elif args.command == 'config':
            show_config()

        elif args.command == 'enable':
            target = resolve_target_config(args.scope)
            if not enable_servers(args.servers, dry_run=args.dry_run, target=target):
                sys.exit(1)

        elif args.command == 'disable':
            if not disable_servers(args.servers,
                                   stop_container_flag=not args.keep_container,
                                   dry_run=args.dry_run,
                                   scope_flag=args.scope):
                sys.exit(1)

    except KeyboardInterrupt:
        print("\nInterrupted by user")
        sys.exit(1)
    except Exception as e:
        print_error(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()
