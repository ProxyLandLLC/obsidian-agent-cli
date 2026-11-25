# obsidian-agent-cli

A full-featured command-line interface for [Obsidian](https://obsidian.md/) — manage your vault, capture knowledge, build canvases, and run plugin commands, all from the terminal or from an AI agent.

Includes reusable agent instructions for clients that support tool execution and custom skills or project context.

---

## Workspace layout

```text
YourVault/
├── AI Workspace/
│   ├── Raw/                 # Unprocessed source material
│   ├── Inbox/               # Captures and unassigned canvases
│   ├── Projects/
│   │   └── example/
│   │       └── knowledge-log.md
│   ├── Reference/           # Reference and teaching notes
│   └── registry.json        # Project index
└── Existing user folders/
```

The setup wizard creates the workspace and four subfolders inside an existing vault. Each folder name is configurable. Project registration creates a directory under Projects; teaching commands use Reference; canvases without a specified folder use Inbox. Raw and Inbox are organizational conventions, not automatic processing pipelines.

Use a dedicated test vault first. The workspace is an organizational convention, **not a security sandbox**: commands accepting explicit paths and vault-wide operations can affect other files. Restrict the agent's OS permissions and review destructive or bulk operations.

This version uses a new registry format. Older workspace layouts are not migrated. Choose a fresh workspace name if an older registry exists. Existing files are not automatically deleted or moved.

---

## Features

| Command group | What it does |
|---------------|-------------|
| `note` | Create, read, update, patch, delete notes — including surgical heading-level edits |
| `search` | Full-text search and Dataview DQL queries |
| `active` | Read/write the note currently open in Obsidian |
| `periodic` | Daily, weekly, monthly notes — read, write, patch, navigate |
| `workspace` | AI workspace project registry and knowledge log |
| `canvas` | Build and manage Obsidian canvas files from JSON specs |
| `excalidraw` | Build Excalidraw diagrams from JSON specs |
| `kanban` | Create and manage Kanban boards |
| `vault` | Find notes by glob pattern, move/rename files |
| `tags` | Rename tags across the entire vault |
| `batch` | Bulk frontmatter edits and find-and-replace |
| `export` | Bundle notes into a single markdown file |
| `teach` | Write reference/teaching notes into the vault |
| `git` | Obsidian Git plugin commands |
| `tasks` | Tasks plugin — add and list tasks with emoji markers |
| `template` | Templater plugin commands |
| `lint` | Obsidian Linter commands |
| `quickadd` | QuickAdd plugin — open modal or run a choice |
| `refactor` | Rename, extract headings, merge notes |
| `mover` | Auto Note Mover — check and trigger rules |
| `meta` | Metadata Menu — get/set frontmatter fields |
| `core` | Core Obsidian UI — palette, graph, settings, splits |
| `uri` | Obsidian URI scheme — works without Obsidian open |
| `status` | REST API health check |
| `config` | View and update CLI configuration |
| `commands` | List and run any Obsidian command by ID |

**Structured results.** Most operational commands emit JSON; interactive setup, help and some errors emit text. Inspect both exit status and the returned error field.

**Dual-mode transport.** Commands try the Obsidian REST API first. File read/write/list/delete operations support filesystem fallback when the REST API is unavailable. Search, patch and UI/plugin commands may require the running app.

---

## Requirements and installation

- Python 3.10 or newer
- An existing local vault directory
- Obsidian desktop and its [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) plugin for API-dependent commands

Install from the source checkout:

```bash
git clone https://github.com/ProxyLandLLC/obsidian-agent-cli.git
cd obsidian-agent-cli
python -m venv .venv
# Activate the virtual environment for your shell first.
python -m pip install .
obsidian-agent --help
obsidian-agent config init
obsidian-agent config show
```

Setup prompts for the vault directory, workspace and subfolder names, optional API key, API URL and TLS verification. With Obsidian and the REST API enabled, run `obsidian-agent status` to inspect connectivity.

See the [installation guide](docs/INSTALL.md) for platform-specific activation and testing instructions.

---

## Quick Start

```bash
# Create a note
obsidian-agent note create "AI Workspace/Projects/my-app/arch.md" --content "# Architecture"

# Read it back
obsidian-agent note read "AI Workspace/Projects/my-app/arch.md"

# Search across vault
obsidian-agent search simple "authentication"

# Register a project for AI knowledge tracking
obsidian-agent workspace project register my-app

# Log a discovery
obsidian-agent workspace log my-app "Auth uses RS256 JWTs. Token expiry is 15 min."

# Read back everything the agent knows about this project
obsidian-agent workspace recall my-app

# Build a canvas overview
obsidian-agent canvas build "my-app-overview" --folder "AI Workspace/Projects/my-app" --spec '{
  "nodes": [
    {"type": "text", "text": "# My App"},
    {"type": "file", "file": "AI Workspace/Projects/my-app/arch.md"}
  ],
  "edges": [
    {"from": 0, "to": 1, "label": "documented in", "color": "4"}
  ]
}'

# Sync vault with git
obsidian-agent git sync -m "feat: update project notes"
```

---

## AI Agent Integration

Load `obsidian_skill.md` using your agent client's supported instruction or skill mechanism. The suggested workflow is to:

1. **Register new projects** on first encounter
2. **Recall prior knowledge** at the start of every session
3. **Log architectural discoveries** and decisions as they happen
4. **Build visual canvases** and **write teaching notes** when asked

See [docs/SKILL_SETUP.md](docs/SKILL_SETUP.md) for details.

---

## Configuration

Configuration is local to the user's home directory at `~/.obsidian-cli/config.json`; the API key is stored separately in `~/.obsidian-cli/.env`. Do not commit or share that file. It is not encrypted.

```bash
obsidian-agent config show
obsidian-agent config init
```

Choose the layout during setup. Changing folder names with `config set` provisions the selected paths but does not move existing content or update existing project registry entries. Use a fresh workspace when changing a populated project layout. Agent instructions must read the actual configured paths before using examples.

---

## Documentation

- [Installation Guide](docs/INSTALL.md)
- [Usage Guide](docs/USAGE.md)
- [AI Skill Setup](docs/SKILL_SETUP.md)

---

## Plugin Commands

Many command groups require optional Obsidian plugins:

| Plugin | Required by |
|--------|------------|
| [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) | API-dependent commands |
| [Dataview](https://github.com/blacksmithgu/obsidian-dataview) | `search advanced`, `note backlinks`, `note by-tag`, `note recent`, `note orphans`, `note links` |
| [Obsidian Git](https://github.com/denolehov/obsidian-git) | `git` commands |
| [Tasks](https://github.com/obsidian-tasks-group/obsidian-tasks) | `tasks ui`, `tasks toggle` |
| [Templater](https://github.com/SilentVoid13/Templater) | `template` commands |
| [Linter](https://github.com/platers/obsidian-linter) | `lint` commands |
| [QuickAdd](https://github.com/chhoumann/quickadd) | `quickadd` commands |
| [Auto Note Mover](https://github.com/farux/obsidian-auto-note-mover) | `mover` commands |
| [Metadata Menu](https://github.com/mdelobelle/metadatamenu) | `meta` commands |
| [Excalidraw](https://github.com/zsviczian/obsidian-excalidraw-plugin) | `excalidraw` commands |
| [Kanban](https://github.com/mgmeyers/obsidian-kanban) | `kanban archive` |

Filesystem-supported operations can work without Obsidian running; check individual command requirements.

---

## License

MIT (declared in package metadata; license notice to be finalized before release).
