# Contributing to mcpctl

Thank you for your interest in contributing to mcpctl! This document provides guidelines and instructions for contributing.

> **⚠️ SECURITY NOTICE**
>
> When contributing server configurations or testing servers from registries, remember that MCP servers can access system resources, files, and network. Always test in a safe environment and verify server behavior before adding to documentation or examples.

## 🚀 Quick Start

1. Fork the repository
2. Clone your fork: `git clone https://github.com/savitojs/mcpctl.git`
3. Create a feature branch: `git checkout -b feature/amazing-feature`
4. Make your changes
5. Test your changes manually with `mcpctl` commands
6. Commit using [Conventional Commits](https://www.conventionalcommits.org/): `git commit -m 'feat: add amazing feature'`
7. Push: `git push origin feature/amazing-feature`
8. Open a Pull Request

## 📋 Development Setup

```bash
# Clone the repository
git clone https://github.com/savitojs/mcpctl.git
cd mcpctl

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install in development mode
pip install -e .
```

## 🧪 Testing Your Changes

Manually test your changes with real MCP servers:

```bash
# Test listing servers
mcpctl list

# Test enabling a server
mcpctl enable filesystem

# Test status checking
mcpctl status

# Test disabling a server
mcpctl disable filesystem
```

## 📚 Configuration Files

mcpctl uses configuration files stored in `~/.config/mcpctl/`:
- `mcp-servers.yaml` - User's MCP server configurations

This file is automatically created on first run with sensible defaults.

## 📚 Adding New MCP Server Configurations

To add a new MCP server configuration:

1. **Add to your local config at `~/.config/mcpctl/mcp-servers.yaml`**:

```yaml
your-server:
  type: npm  # or docker, python, executable
  description: "Brief description of what the server does"
  transport: stdio
  requires_container: false  # or true if needs Docker
  mcp_config:
    command: npx
    args:
      - -y
      - "@org/your-mcp-server"
    env:
      API_KEY: "${YOUR_API_KEY}"  # If required
  env_vars:
    - YOUR_API_KEY  # List required env vars
```

2. **Test the configuration**:

```bash
# Edit your local config
vi ~/.config/mcpctl/mcp-servers.yaml

# Test enabling
mcpctl enable your-server

# Test status
mcpctl status your-server

# Test disabling
mcpctl disable your-server
```

3. **Document environment variables**:

Add to README.md if the server requires API keys or environment variables.

4. **Submit PR** with:
   - Server configuration
   - Description of what it does
   - Required environment variables
   - Any special setup instructions

## 🐛 Reporting Bugs

When reporting bugs, please include:

1. **Description**: Clear description of the bug
2. **Steps to reproduce**: Minimal steps to reproduce the issue
3. **Expected behavior**: What you expected to happen
4. **Actual behavior**: What actually happened
5. **Environment**:
   - OS (Linux, macOS, Windows)
   - Python version (`python --version`)
   - Docker version (`docker --version`)
   - mcpctl version
6. **Logs**: Relevant error messages or logs

## 💡 Feature Requests

We welcome feature requests! Please:

1. Check existing issues first
2. Clearly describe the feature
3. Explain the use case
4. Provide examples if possible

## 🔍 Code Review Process

1. All submissions require review
2. Reviewers will check:
   - Code quality and style
   - Tests and documentation
   - Backward compatibility
3. Address review comments
4. Once approved, maintainers will merge

## 📦 Release Process

(For maintainers)

Releases are automated using [release-please](https://github.com/googleapis/release-please):

1. Merge PRs with conventional commit messages (`feat:`, `fix:`, `docs:`, etc.)
2. Release-please creates/updates a release PR automatically
3. Review and merge the release PR
4. Release-please creates a GitHub release and git tag
5. GitHub Actions automatically publishes to PyPI

## 📄 License

By contributing, you agree that your contributions will be licensed under the MIT License.

## ❓ Questions?

- Open a [Discussion](https://github.com/savitojs/mcpctl/discussions)
- Ask in [Issues](https://github.com/savitojs/mcpctl/issues)

## 🙏 Thank You!

Your contributions make mcpctl better for everyone!
