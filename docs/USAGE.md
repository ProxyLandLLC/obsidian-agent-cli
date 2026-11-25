# Usage Guide

## Core Concepts

**Structured output.** Most operational commands return JSON. Setup, help and some errors use text; check exit status and the error field.

```json
// Success
{"ok": true, "transport": "api"}
{"content": "# My Note\n\n...", "transport": "fs"}

// Error
{"error": true, "message": "Note not found: AI Workspace/missing.md"}
```

**Dual-mode transport.** Commands try the Obsidian REST API first (requires Obsidian open). File read/write/list/delete support filesystem fallback. Search, patch and many UI commands require the API. When present, the transport field identifies the selected transport.

**Supply vault-relative paths.** Never use absolute paths in arguments — use `AI Workspace/my-note.md`, not `C:\Users\...\AI Workspace\my-note.md`.

---

Use `obsidian-agent config show` to discover configured paths. The examples assume default folder names. Raw and Inbox are conventions; Projects contains registered project logs and Reference receives teaching notes. The workspace is not a sandbox; avoid bulk or destructive actions without explicit approval.

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
obsidian-agent note create "AI Workspace/Projects/my-project/arch.md" --content "# Architecture"

# Read
obsidian-agent note read "AI Workspace/Projects/my-project/arch.md"

# Append to a specific heading
obsidian-agent note patch "AI Workspace/Projects/my-project/arch.md" "New dependency: redis" \
  --target "Dependencies" --operation append --create-if-missing

# Read metadata (frontmatter, tags, file stat)
obsidian-agent note meta "AI Workspace/Projects/my-project/arch.md"

# Read document map (headings, blocks, frontmatter fields)
obsidian-agent note map "AI Workspace/Projects/my-project/arch.md"
```

### Work with today's daily note

```bash
obsidian-agent periodic today                              # read it
obsidian-agent periodic append daily "- Standup done"     # append a line
obsidian-agent periodic patch daily "done" \
  --target "Tasks" --operation replace              # replace a heading section
obsidian-agent periodic nav daily next                    # open next day in Obsidian
```

### Search the vault

```bash
obsidian-agent search simple "authentication middleware"
obsidian-agent search advanced "TABLE file.mtime FROM \"AI Workspace\" SORT file.mtime DESC LIMIT 10"
obsidian-agent note backlinks "AI Workspace/Projects/auth.md"
obsidian-agent note by-tag "#project"
obsidian-agent note recent --limit 20
```

### AI workspace knowledge

```bash
# Register a new project (run once)
obsidian-agent workspace project register my-app

# Read everything known about a project (run at session start)
obsidian-agent workspace recall my-app

# Log a discovery mid-session
obsidian-agent workspace log my-app "Auth uses RS256 JWTs. Expiry is 15 min."
obsidian-agent workspace log my-app "Decision: kept Postgres over MongoDB — team familiarity"

# Check all registered projects
obsidian-agent workspace status
```

### Build a canvas overview

```bash
obsidian-agent canvas build "my-app-overview" --folder "AI Workspace/Projects/my-app" --spec '{
  "nodes": [
    {"type": "text", "text": "# My App"},
    {"type": "file", "file": "AI Workspace/Projects/my-app/arch.md"},
    {"type": "file", "file": "AI Workspace/Projects/my-app/decisions.md"}
  ],
  "edges": [
    {"from": 0, "to": 1, "label": "documented in", "color": "4"},
    {"from": 0, "to": 2, "label": "decisions", "color": "5"}
  ]
}'
obsidian-agent canvas open "AI Workspace/Projects/my-app/my-app-overview.canvas"
```

### Bulk operations

```bash
# Rename a tag everywhere — preview first, then apply
obsidian-agent tags rename "#todo" "#task" --dry-run
obsidian-agent tags rename "#todo" "#task"

# Set a frontmatter field in all notes in a folder
obsidian-agent batch frontmatter status archived --folder "AI Workspace/Projects" --dry-run
obsidian-agent batch frontmatter status archived --folder "AI Workspace/Projects"

# Find and replace text across notes
obsidian-agent batch rename "OldCompanyName" "NewCompanyName" --folder "AI Workspace"
obsidian-agent batch rename "\b2024\b" "2025" --folder "AI Workspace" --regex --dry-run
```

### Find and move files

```bash
# Find all notes matching a pattern
obsidian-agent vault find "**/*meeting*.md" --folder "AI Workspace"

# Move/rename a note
obsidian-agent vault move "AI Workspace/Inbox/rough-idea.md" "AI Workspace/Projects/my-app/idea.md"
```

### Export for AI context

```bash
# Bundle an entire folder into one markdown file
obsidian-agent export bundle context.md --folder "AI Workspace/Projects/my-app"
# Then feed context.md to an AI tool
```

### Active note (what's open in Obsidian right now)

```bash
obsidian-agent active read
obsidian-agent active append "- New bullet point"
obsidian-agent active patch "in progress" \
  --target "status" --target-type frontmatter --operation replace
```

---

## Tips

**Pipe JSON through `jq` for readable output (on machines with jq):**
```bash
obsidian-agent note meta "AI Workspace/note.md" | jq '.frontmatter'
obsidian-agent workspace recall my-app | jq '.content'
```

**The `--dry-run` flag** is available on all destructive batch/tag commands. Always use it first.

**Plugin commands that need Obsidian open:** `active`, `periodic`, `quickadd`, `git`, `tasks`, `template`, `lint`, `meta ui`, `core`, `kanban archive`. Everything else works without Obsidian open.
