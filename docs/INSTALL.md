# Installation guide

## Prerequisites

Python 3.10+ and an existing vault directory. For live API operations, install Obsidian desktop and enable the Local REST API community plugin. Use a separate test vault for initial setup.

## Install from source

```bash
git clone https://github.com/ProxyLandLLC/obsidian-agent-cli.git
cd obsidian-agent-cli
python -m venv .venv
```

Activate the environment: macOS/Linux (`source .venv/bin/activate`), Windows PowerShell (`.\.venv\Scripts\Activate.ps1`). Alternatively run Python and the installed CLI directly from that environment.

```bash
python -m pip install .
obsidian-agent --help
obsidian-agent config init
```

| Setup prompt | Default or input |
|---|---|
| Vault path | Existing local directory chosen by the user |
| Workspace path | AI Workspace |
| Raw folder | Raw |
| Inbox folder | Inbox |
| Projects folder | Projects |
| Reference folder | Reference |
| Local REST API key | Optional for offline commands; hidden input |
| API URL | http://127.0.0.1:27123 (match your plugin settings) |
| Verify TLS certificates | Yes for HTTPS |

Folder names must be distinct within the workspace, portable single directory names. Setup creates the directories and registry without overwriting notes. Existing legacy registries are unsupported; choose a fresh workspace. No migration or deletion is performed.

## Verify

```bash
obsidian-agent config show
obsidian-agent workspace status
obsidian-agent workspace project register example
obsidian-agent workspace log example "First test entry"
obsidian-agent workspace recall example
```

Check the configured Projects folder for the example knowledge log. For live API access, enable the plugin and run `obsidian-agent status`. API search, patch and UI/plugin commands require a reachable compatible API.

Keep the local API key private. Prefer localhost; do not expose an unauthenticated API or disable TLS verification for remote connections. The local configuration is not encrypted. The workspace does not restrict the agent's filesystem access.

## Run tests

From the repository root:

```bash
python -m pip install -e .
python -m pip install pytest
python -m pytest -q
```

The automated tests use temporary vaults and mocks. A real Obsidian integration smoke test is still recommended before using important data.
