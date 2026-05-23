# Usage Guide

## Core Concepts

**All commands output JSON.** Every command prints a single JSON object to stdout — parse it, pipe it, or just read it.

```json
// Success
{"ok": true, "transport": "api"}
{"content": "# My Note\n\n...", "transport": "fs"}

// Error
{"error": true, "message": "Note not found: AI Workspace/missing.md"}
```

**Dual-mode transport.** Commands try the Obsidian REST API first (requires Obsidian open). If the API is unavailable, most commands fall back to reading/writing the vault filesystem directly. The `"transport"` field in every response tells you which was used.

**Vault paths are always relative to the vault root.** Never use absolute paths in arguments — use `AI Workspace/my-note.md`, not `C:\Users\...\AI Workspace\my-note.md`.

---

## Command Groups

| Group | Purpose |
|-------|---------|
| `note` | Create, read, update, delete, patch notes |
| `search` | Search vault by text or Dataview DQL |
| `active` | Read/write the note currently open in Obsidian |
| `periodic` | Daily, weekly, monthly notes — read, write, patch, navigate |
| `workspace` | AI workspace project registry and knowledge log |
| `canvas` | Build and manage Obsidian canvas files |
| `excalidraw` | Build Excalidraw diagrams from specs |
| `kanban` | Create and manage Kanban boards |
| `vault` | Find notes by glob pattern, move/rename files |
| `tags` | Rename tags across the entire vault |
| `batch` | Bulk frontmatter edits and find-and-replace |
| `export` | Bundle notes into a single markdown file |
| `teach` | Write teaching notes into the vault |
| `git` | Obsidian Git plugin commands |
| `tasks` | Tasks plugin — add tasks with emoji markers |
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

---

## Common Workflows

### Read and write notes

```bash
# Create
obsidian note create "AI Workspace/Projects/my-project/arch.md" --content "# Architecture"

# Read
obsidian note read "AI Workspace/Projects/my-project/arch.md"

# Append to a specific heading
obsidian note patch "AI Workspace/Projects/my-project/arch.md" "New dependency: redis" \
  --target "Dependencies" --operation append --create-if-missing

# Read metadata (frontmatter, tags, file stat)
obsidian note meta "AI Workspace/Projects/my-project/arch.md"

# Read document map (headings, blocks, frontmatter fields)
obsidian note map "AI Workspace/Projects/my-project/arch.md"
```

### Work with today's daily note

```bash
obsidian periodic today                              # read it
obsidian periodic append daily "- Standup done"     # append a line
obsidian periodic patch daily "done" \
  --target "Tasks" --operation replace              # replace a heading section
obsidian periodic nav daily next                    # open next day in Obsidian
```

### Search the vault

```bash
obsidian search simple "authentication middleware"
obsidian search advanced "TABLE file.mtime FROM \"AI Workspace\" SORT file.mtime DESC LIMIT 10"
obsidian note backlinks "AI Workspace/Projects/auth.md"
obsidian note by-tag "#project"
obsidian note recent --limit 20
```

### AI workspace knowledge

```bash
# Register a new project (run once)
obsidian workspace project register my-app

# Read everything known about a project (run at session start)
obsidian workspace recall my-app

# Log a discovery mid-session
obsidian workspace log my-app "Auth uses RS256 JWTs. Expiry is 15 min."
obsidian workspace log my-app "Decision: kept Postgres over MongoDB — team familiarity"

# Check all registered projects
obsidian workspace status
```

### Build a canvas overview

```bash
obsidian canvas build "my-app-overview" --spec '{
  "nodes": [
    {"type": "text", "text": "# My App"},
    {"type": "file", "file": "AI Workspace/my-app/arch.md"},
    {"type": "file", "file": "AI Workspace/my-app/decisions.md"}
  ],
  "edges": [
    {"from": 0, "to": 1, "label": "documented in", "color": "4"},
    {"from": 0, "to": 2, "label": "decisions", "color": "5"}
  ]
}'
obsidian canvas open "AI Workspace/my-app/my-app-overview.canvas"
```

### Bulk operations

```bash
# Rename a tag everywhere — preview first, then apply
obsidian tags rename "#todo" "#task" --dry-run
obsidian tags rename "#todo" "#task"

# Set a frontmatter field in all notes in a folder
obsidian batch frontmatter status archived --folder "AI Workspace/OldProjects" --dry-run
obsidian batch frontmatter status archived --folder "AI Workspace/OldProjects"

# Find and replace text across notes
obsidian batch rename "OldCompanyName" "NewCompanyName" --folder "AI Workspace"
obsidian batch rename "\b2024\b" "2025" --folder "AI Workspace" --regex --dry-run
```

### Find and move files

```bash
# Find all notes matching a pattern
obsidian vault find "**/*meeting*.md" --folder "AI Workspace"

# Move/rename a note
obsidian vault move "AI Workspace/inbox/rough-idea.md" "AI Workspace/Projects/my-app/idea.md"
```

### Export for AI context

```bash
# Bundle an entire folder into one markdown file
obsidian export bundle context.md --folder "AI Workspace/my-app"
# Then feed context.md to an AI tool
```

### Active note (what's open in Obsidian right now)

```bash
obsidian active read
obsidian active append "- New bullet point"
obsidian active patch "in progress" \
  --target "status" --target-type frontmatter --operation replace
```

---

## Tips

**Pipe JSON through `jq` for readable output (on machines with jq):**
```bash
obsidian note meta "AI Workspace/note.md" | jq '.frontmatter'
obsidian workspace recall my-app | jq '.entries[-3:]'
```

**The `--dry-run` flag** is available on all destructive batch/tag commands. Always use it first.

**Plugin commands that need Obsidian open:** `active`, `periodic`, `quickadd`, `git`, `tasks`, `template`, `lint`, `meta ui`, `core`, `kanban archive`. Everything else works without Obsidian open.
