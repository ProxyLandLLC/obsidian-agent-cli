---
name: "obsidian-agent-cli"
description: >-
  Full-featured command-line interface for Obsidian — manage notes, canvases,
  Excalidraw diagrams, Kanban boards, periodic notes, git, tasks, and more.
  Includes an AI agent skill for persistent knowledge capture across sessions.
---

# obsidian-agent-cli

A full-featured CLI for [Obsidian](https://obsidian.md/) that lets you manage your vault from the terminal. Designed for both direct use and AI agent integration — agents can register projects, log architectural discoveries, and recall prior knowledge across sessions.

## Installation

```bash
pip install obsidian-agent-cli
```

**Prerequisites:**
- Python 3.10+
- [Obsidian](https://obsidian.md/) desktop app
- [Local REST API](https://github.com/coddingtonbear/obsidian-local-rest-api) community plugin (installed and enabled in Obsidian)

**Setup:**
```bash
obsidian config init
```

You'll be prompted for your vault path, workspace folder name, REST API URL, and API key.

## Usage

### Basic Commands

```bash
# Verify connection
obsidian status

# Create a note
obsidian note create "AI Workspace/my-project/arch.md" --content "# Architecture"

# Read a note
obsidian note read "AI Workspace/my-project/arch.md"

# Search the vault
obsidian search simple "authentication"
```

### Dual-Mode Transport

Commands try the Obsidian REST API first. If Obsidian isn't running, most commands fall back to the vault filesystem directly. Every response includes a `"transport"` field indicating which was used (`"api"` or `"fs"`).

All commands output JSON:
```json
{"ok": true, "transport": "api"}
{"content": "# My Note\n\n...", "transport": "fs"}
{"error": true, "message": "Note not found: AI Workspace/missing.md"}
```

## Command Groups

### Workspace (AI Knowledge)

AI agent project registry and persistent knowledge log.

| Command | Description |
|---------|-------------|
| `workspace project register <name>` | Register a new project |
| `workspace recall <name>` | Read everything known about a project |
| `workspace log <name> "<text>"` | Log a discovery or decision |
| `workspace status` | List all registered projects |

### Notes

| Command | Description |
|---------|-------------|
| `note create <path>` | Create a note |
| `note read <path>` | Read a note |
| `note update <path>` | Overwrite or append to a note |
| `note patch <path>` | Surgical heading/frontmatter edit |
| `note delete <path>` | Delete a note |
| `note meta <path>` | Read frontmatter, tags, file stat |
| `note map <path>` | Read document structure (headings, blocks) |
| `note list <folder>` | List notes in a folder |
| `note backlinks <path>` | Notes linking to this note (Dataview) |
| `note recent` | Recently modified notes (Dataview) |
| `note by-tag <tag>` | Notes with a given tag (Dataview) |

### Search

| Command | Description |
|---------|-------------|
| `search simple <query>` | Full-text search across vault |
| `search advanced <dql>` | Dataview DQL query |
| `search tags` | List all tags in vault |

### Canvas

| Command | Description |
|---------|-------------|
| `canvas build <name> --spec <json>` | Build a canvas from a JSON spec |
| `canvas read <path>` | Read canvas structure |
| `canvas add-node <path>` | Add a node to existing canvas |
| `canvas open <path>` | Open canvas in Obsidian |

### Excalidraw

| Command | Description |
|---------|-------------|
| `excalidraw build <path> --spec <json>` | Build diagram from spec |
| `excalidraw create <path>` | Create empty drawing |
| `excalidraw add-shape <path>` | Add shape to drawing |
| `excalidraw read <path>` | Read drawing structure |

### Kanban

| Command | Description |
|---------|-------------|
| `kanban create <path>` | Create a Kanban board |
| `kanban card add <path> <lane> <text>` | Add a card to a lane |
| `kanban lane add <path> <name>` | Add a lane |
| `kanban read <path>` | Read board structure |

### Periodic Notes

| Command | Description |
|---------|-------------|
| `periodic today` | Read today's daily note |
| `periodic get <period>` | Read current weekly/monthly note |
| `periodic append <period> <text>` | Append to current note |
| `periodic patch <period> <text>` | Edit a heading section |
| `periodic nav <period> prev\|next` | Navigate to adjacent note |

### Active Note

| Command | Description |
|---------|-------------|
| `active read` | Read note currently open in Obsidian |
| `active write <content>` | Overwrite active note |
| `active append <content>` | Append to active note |
| `active patch <content>` | Surgical edit on active note |
| `active meta` | Frontmatter + tags of active note |

### Vault

| Command | Description |
|---------|-------------|
| `vault find <glob>` | Find notes by glob pattern |
| `vault move <src> <dst>` | Move or rename a note |

### Batch

| Command | Description |
|---------|-------------|
| `batch frontmatter <field> <value>` | Set frontmatter field across notes |
| `batch rename <old> <new>` | Find-and-replace across notes |

### Tags

| Command | Description |
|---------|-------------|
| `tags rename <old> <new>` | Rename a tag across entire vault |

### Export

| Command | Description |
|---------|-------------|
| `export bundle <output>` | Bundle notes into a single markdown file |

### Teach

| Command | Description |
|---------|-------------|
| `teach write <title>` | Write a reference/teaching note |
| `teach list` | List all teaching notes |

### Plugin Commands

| Command | Description |
|---------|-------------|
| `git sync` | Commit + push via Obsidian Git plugin |
| `tasks add <text>` | Add task with emoji markers |
| `tasks list` | List tasks in vault |
| `template insert` | Open Templater insert modal |
| `lint` | Lint active file via Obsidian Linter |
| `quickadd run <name>` | Run a QuickAdd choice |
| `refactor rename <path> <name>` | Rename a note |
| `meta get <path> <field>` | Get a frontmatter field value |
| `meta set <path> <field> <value>` | Set a frontmatter field value |
| `core palette` | Open Obsidian command palette |
| `commands run <id>` | Run any Obsidian command by ID |

## Examples

### Register a project and recall prior knowledge

```bash
# First time on a project
obsidian workspace project register my-app

# Every subsequent session — read this before doing anything
obsidian workspace recall my-app
```

### Log a discovery mid-session

```bash
obsidian workspace log my-app "Auth uses RS256 JWTs. Token expiry is 15 min."
obsidian workspace log my-app "Decision: kept Postgres over MongoDB — team familiarity"
```

### Build a canvas overview

```bash
obsidian canvas build "my-app-overview" --spec '{
  "nodes": [
    {"type": "text", "text": "# My App"},
    {"type": "file", "file": "AI Workspace/my-app/arch.md"}
  ],
  "edges": [
    {"from": 0, "to": 1, "label": "documented in", "color": "4"}
  ]
}'
```

### Bulk operations with dry-run

```bash
obsidian tags rename "#todo" "#task" --dry-run
obsidian tags rename "#todo" "#task"

obsidian batch frontmatter status archived --folder "AI Workspace/OldProjects" --dry-run
obsidian batch frontmatter status archived --folder "AI Workspace/OldProjects"
```

## For AI Agents

Drop `obsidian_skill.md` (included in this repo) into your project root. Your AI agent will automatically:

1. **Register new projects** on first encounter
2. **Recall prior knowledge** at the start of every session
3. **Log architectural discoveries** and decisions as they happen
4. **Build visual canvases** and **write teaching notes** when asked

When using this CLI programmatically:

1. **All commands output JSON** — always parse stdout, never scrape text
2. **Check the `"error"` key** before using any other field
3. **Check the `"transport"` key** — `"api"` means Obsidian is running, `"fs"` means filesystem fallback
4. **Vault paths are always relative to vault root** — never use absolute paths in arguments
5. **Use `--dry-run`** on all `batch` and `tags` commands before applying changes
6. **Run `obsidian workspace recall <project>`** at session start before touching any code

## More Information

- Full documentation: See `docs/` in the repository
- AI agent skill file: See `obsidian_skill.md` in the repository
- Source: [https://github.com/ProxyLandLLC/obsidian-agent-cli](https://github.com/ProxyLandLLC/obsidian-agent-cli)

## Version

0.1.0
