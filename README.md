# obsidian-agent-cli

A full-featured command-line interface for [Obsidian](https://obsidian.md/) — manage your vault, capture knowledge, build canvases, and run plugin commands, all from the terminal or from an AI agent.

Works with any AI coding assistant (Claude Code, Codex, Gemini CLI, etc.) via the included `obsidian_skill.md`.

---

## How It Works: Vault Structure

The CLI is designed around a clean separation of concerns inside your vault:

```
MyVault/                        ← your Obsidian vault root
├── .obsidian/
│
├── AI Workspace/               ← the AI agent's dedicated folder (managed by this CLI)
│   ├── registry.json           #   project registry
│   ├── my-project/             #   per-project knowledge
│   │   └── knowledge-log.md
│   └── Teaching Notes/         #   reference notes written by the agent
│
├── Your Notes/                 ← your folders — the AI never touches these
├── Projects/                   ← yours
└── Journal/                    ← yours
```

**The AI only operates inside `AI Workspace/`.** Every note, canvas, log, and registry file it creates lives there. Your own folders are completely untouched unless you explicitly pass their paths to a command.

> 💡 **Recommended setup:** Create a dedicated Obsidian vault just for this — don't drop it into an existing vault you already use heavily. A fresh vault keeps things clean. Then `AI Workspace/` is one subfolder inside it, and any other top-level folders you create are entirely yours.

The `AI Workspace` folder name is just the default — rename it to anything you like:
```bash
obsidian config set workspace_path "My AI Zone"
```

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

**All commands output JSON.** Every command returns a single JSON object — parse it, pipe it, or feed it to an AI agent.

**Dual-mode transport.** Commands try the Obsidian REST API first. If Obsidian isn't running, most commands fall back to the vault filesystem directly.

---

## Requirements

- Python 3.10+
- [Obsidian](https://obsidian.md/) desktop app
- [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) community plugin (installed and enabled inside Obsidian)

---

## Installation

```bash
pip install obsidian-agent-cli
```

Then run the setup wizard:

```bash
obsidian config init
```

You'll be prompted for:
- Your vault path (e.g. `/home/yourname/Documents/MyVault`)
- Your workspace folder name (default: `AI Workspace`)
- The REST API URL (default: `http://127.0.0.1:27123`)
- Your Local REST API key (copy from Obsidian → Settings → Local REST API)

### Verify it works

With Obsidian open:
```bash
obsidian status
```

You should see:
```json
{"ok": true, "versions": {"obsidian": "1.x.x"}, "transport": "api"}
```

---

## Quick Start

```bash
# Create a note
obsidian note create "Projects/my-app/arch.md" --content "# Architecture"

# Read it back
obsidian note read "Projects/my-app/arch.md"

# Search across vault
obsidian search simple "authentication"

# Register a project for AI knowledge tracking
obsidian workspace project register my-app

# Log a discovery
obsidian workspace log my-app "Auth uses RS256 JWTs. Token expiry is 15 min."

# Read back everything the agent knows about this project
obsidian workspace recall my-app

# Build a canvas overview
obsidian canvas build "my-app-overview" --spec '{
  "nodes": [
    {"type": "text", "text": "# My App"},
    {"type": "file", "file": "Projects/my-app/arch.md"}
  ],
  "edges": [
    {"from": 0, "to": 1, "label": "documented in", "color": "4"}
  ]
}'

# Sync vault with git
obsidian git sync -m "feat: update project notes"
```

---

## AI Agent Integration

Drop `obsidian_skill.md` into any project root. Your AI agent (Claude Code, Codex, Gemini CLI, etc.) will automatically:

1. **Register new projects** on first encounter
2. **Recall prior knowledge** at the start of every session
3. **Log architectural discoveries** and decisions as they happen
4. **Build visual canvases** and **write teaching notes** when asked

See [docs/SKILL_SETUP.md](docs/SKILL_SETUP.md) for details.

---

## Configuration

Config is stored in `~/.obsidian-cli/config.json`. You can edit it with `obsidian config`:

```bash
obsidian config show                              # view current config
obsidian config set vault_path /path/to/vault    # update vault path
obsidian config set workspace_path "MyWorkspace"  # rename workspace folder
obsidian config set api_key YOUR_KEY             # update API key
obsidian config init                             # re-run setup wizard
```

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
| [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) | Everything (core dependency) |
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

Commands that don't require a plugin work directly on the filesystem and don't need Obsidian to be open.

---

## License

MIT
