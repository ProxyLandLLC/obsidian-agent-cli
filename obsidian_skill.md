---
name: obsidian-vault
description: Use when working on any software project — manages knowledge capture, canvas creation, and reference notes in the user's Obsidian vault via the obsidian CLI
triggers:
  - starting work on a project
  - discovering architectural decisions
  - user asks for visual overview
  - user asks for explanation of something
---

# Obsidian Vault Skill

This skill gives you access to the user's Obsidian vault as a persistent knowledge store.
The `obsidian` CLI must be globally installed and configured. All commands output JSON.

Before using any command, verify the CLI is connected:
```bash
obsidian status
```
If you see `"ok": true`, you're ready. If not, ask the user to run `obsidian config init`.

## Vault Layout

The vault is configured by the user during `obsidian config init`. The default workspace layout is:

- Workspace folder: `AI Workspace/`
- Teaching notes: `AI Workspace/Teaching Notes/`
- Per-project folders: `AI Workspace/<project-name>/`
- Registry: `AI Workspace/registry.json`

The workspace folder name can be changed with `obsidian config set workspace_path "YourFolder"`.

## When To Use This Skill

### Auto-trigger (do these without being asked):

**At the start of a session on a registered project:**
```bash
obsidian workspace recall <project-name>
```
Read this output before proceeding. It contains everything previously logged about this project.

**First time touching a new project:**
```bash
obsidian workspace project register <project-name>
```

**After discovering something architecturally significant** (design patterns, tech choices, gotchas, key files):
```bash
obsidian workspace log <project-name> "<what you discovered>"
```

**After making or explaining a significant decision:**
```bash
obsidian workspace log <project-name> "Decision: <decision and reason>"
```

### On-demand only (only when user explicitly asks):

**When user asks you to explain something:**
```bash
obsidian teach write "<Topic Title>" --content "<markdown explanation>"
```

**When user asks for a visual overview of the codebase or a feature:**
```bash
obsidian canvas build "<project>-overview" --spec '<json spec>'
obsidian canvas open "AI Workspace/<project>/<name>.canvas"
```

## When NOT To Use This Skill

- Trivial changes: typo fixes, minor formatting, single-line edits
- Don't write teaching notes unless explicitly asked
- Don't build canvases for small or single-file changes
- Don't log things already in the knowledge log

## Command Reference

### Knowledge capture
```bash
# Register a project (run once per project)
obsidian workspace project register my-project

# Read back everything known about a project (run at session start)
obsidian workspace recall my-project

# Log a discovery or decision
obsidian workspace log my-project "Auth middleware uses JWT. Token expiry is 24h."

# Check all project status
obsidian workspace status
```

### Notes
```bash
# Create a note
obsidian note create "AI Workspace/my-project/arch.md" --content "# Architecture\n\n..."

# Read a note
obsidian note read "AI Workspace/my-project/arch.md"

# Append to a note
obsidian note update "AI Workspace/my-project/arch.md" "New content" --append

# Surgical edit — append to a specific heading
# Flags: --create-if-missing  --apply-if-preexists  --trim-whitespace
obsidian note patch "AI Workspace/my-project/arch.md" "New line" \
  --operation append --target-type heading --target "Dependencies"

# List notes in a folder
obsidian note list "AI Workspace/my-project"

# Open a note in Obsidian UI
obsidian note open "AI Workspace/my-project/arch.md"

# Note metadata (frontmatter, tags, stat)
obsidian note meta "AI Workspace/my-project/arch.md"
obsidian note meta "AI Workspace/my-project/arch.md" --frontmatter   # slice to frontmatter only
obsidian note meta "AI Workspace/my-project/arch.md" --tags           # tags only
obsidian note meta "AI Workspace/my-project/arch.md" --stat           # file stat only

# Note map (patch targets: headings, blocks, frontmatter fields)
obsidian note map "AI Workspace/my-project/arch.md"

# DQL shortcuts (require Dataview plugin)
obsidian note backlinks "AI Workspace/my-project/arch.md"   # notes linking to this note
obsidian note recent --limit 20                       # recently modified notes
obsidian note by-tag "#project"                       # notes with a given tag
obsidian note links "AI Workspace/my-project/arch.md"        # notes this note links to
obsidian note orphans                                  # notes with no incoming links
```

### Search
```bash
# Fuzzy search across vault
obsidian search simple "authentication"

# Dataview DQL (requires Dataview plugin)
obsidian search advanced "TABLE file.mtime FROM \"AI Workspace\" SORT file.mtime DESC LIMIT 10"

# All tags
obsidian search tags
```

### Canvases
```bash
# Build a canvas from a spec (one-shot, preferred approach)
obsidian canvas build "my-project-overview" --spec '{
  "nodes": [
    {"type": "text", "text": "# My Project\nOverview"},
    {"type": "file", "file": "AI Workspace/my-project/arch.md"},
    {"type": "link", "url": "https://github.com/user/repo"}
  ],
  "edges": [
    {"from": 0, "to": 1, "label": "documented in", "color": "4"}
  ]
}'

# Open canvas in Obsidian
obsidian canvas open "AI Workspace/my-project/my-project-overview.canvas"

# Add a node to existing canvas
obsidian canvas add-node "AI Workspace/my-project/overview.canvas" \
  --type file --file "AI Workspace/my-project/new-note.md"

# Read canvas structure
obsidian canvas read "AI Workspace/my-project/overview.canvas"
```

### Teaching notes
```bash
# Write a reference/teaching note (only when user asks)
obsidian teach write "How JWT Works" \
  --content "JWT (JSON Web Token) is..."

# List teaching notes
obsidian teach list

# Open in Obsidian
obsidian teach open "How JWT Works"
```

### Periodic notes
```bash
obsidian periodic today              # read today's daily note
obsidian periodic get weekly         # read this week's note
obsidian periodic write daily "# Today\n\nContent"  # overwrite current note
obsidian periodic append daily "- new item"          # append to current note
obsidian periodic patch daily "done" --target "Tasks" --operation replace
obsidian periodic delete daily                        # delete current note

# Specific date (YYYY-MM-DD format)
obsidian periodic date daily 2026-05-11              # read that day's note
obsidian periodic date daily 2026-05-11 --write "# Content"
obsidian periodic date daily 2026-05-11 --append "- item"
obsidian periodic date daily 2026-05-11 --delete
```

### Active note (currently open in Obsidian)
```bash
obsidian active read             # read content
obsidian active meta             # frontmatter + tags + stat
obsidian active write "# New"   # overwrite
obsidian active append "- item" # append
obsidian active patch "done" --target "Status" --target-type frontmatter --operation replace
obsidian active delete           # delete
```

### Vault file operations
```bash
# Find notes by glob pattern
obsidian vault find "**/*meeting*.md"
obsidian vault find "*.md" --folder "AI Workspace"

# Move or rename a note
obsidian vault move "AI Workspace/old.md" "AI Workspace/new.md"
```

### Tag management
```bash
obsidian tags rename "#todo" "#task"            # rename tag across entire vault
obsidian tags rename "#todo" "#task" --dry-run  # preview changes without modifying files
```

### Server status
```bash
obsidian status   # REST API health, plugin version, Obsidian version, auth status
```

### Export
```bash
# Bundle notes into a single markdown file (useful for AI context)
obsidian export bundle                           # auto-named .md in vault parent dir
obsidian export bundle bundle.md --folder "AI Workspace"
```

### Batch operations (bulk edits across many notes)
```bash
# Set a frontmatter field in all matching notes
obsidian batch frontmatter status active --folder "AI Workspace"
obsidian batch frontmatter status active --folder "AI Workspace" --dry-run

# Find-and-replace text across notes (literal or regex)
obsidian batch rename "Old Name" "New Name" --folder "AI Workspace"
obsidian batch rename "Old Name" "New Name" --folder "AI Workspace" --dry-run
obsidian batch rename "\d{4}-\d{2}-\d{2}" "REDACTED" --folder "AI Workspace" --regex
```

### URI scheme (works without Obsidian running)
```bash
# Create note via URI (opens Obsidian)
obsidian uri new --name "My Note" --folder "AI Workspace/inbox"
obsidian uri new --name "My Note" --content "# Content" --silent --overwrite

# Open Obsidian search UI
obsidian uri search "#project status:active"
```

### Excalidraw drawings
```bash
# Create empty drawing
obsidian excalidraw create "AI Workspace/my-project/diagram.excalidraw"

# One-shot build from spec (preferred approach)
obsidian excalidraw build "AI Workspace/my-project/flow.excalidraw" --spec '{
  "elements": [
    {"type": "rectangle", "label": "Start"},
    {"type": "ellipse", "label": "Process"},
    {"type": "diamond", "label": "Decision?"}
  ],
  "arrows": [
    {"from": 0, "to": 1, "label": "yes"},
    {"from": 1, "to": 2}
  ]
}'

# Add shapes to existing drawing (returns element_id)
obsidian excalidraw add-shape "AI Workspace/diagram.excalidraw" --type rectangle --label "My Box"
obsidian excalidraw add-shape "AI Workspace/diagram.excalidraw" --type ellipse --label "Process"
obsidian excalidraw add-shape "AI Workspace/diagram.excalidraw" --type diamond --label "Decision?"
obsidian excalidraw add-shape "AI Workspace/diagram.excalidraw" --type text --label "Note"

# Connect shapes
obsidian excalidraw add-arrow "AI Workspace/diagram.excalidraw" <from_id> <to_id> --label "flows to"

# Read / open
obsidian excalidraw read "AI Workspace/diagram.excalidraw"
obsidian excalidraw open "AI Workspace/diagram.excalidraw"
```

### Kanban boards
```bash
# Create board
obsidian kanban create "AI Workspace/my-project/board.md" --lanes "To Do,In Progress,Review,Done"

# Read board structure
obsidian kanban read "AI Workspace/my-project/board.md"

# Add/manage cards
obsidian kanban card add "AI Workspace/my-project/board.md" "To Do" "Implement feature X"
obsidian kanban card add "AI Workspace/my-project/board.md" "Done" "Deploy to prod" --done

# Add lane
obsidian kanban lane add "AI Workspace/my-project/board.md" "Blocked"

# Archive done cards (requires Kanban plugin running)
obsidian kanban archive "AI Workspace/my-project/board.md"
```

### Obsidian Git (requires Obsidian Git plugin)
```bash
obsidian git sync                         # commit + push (auto message)
obsidian git sync -m "feat: update notes" # commit + push (specified message)
obsidian git commit                        # commit only
obsidian git pull                          # pull from remote
obsidian git push                          # push to remote
obsidian git status                        # list changed files
obsidian git fetch                         # fetch without merge
obsidian git pause                         # pause/resume auto routines
obsidian git branch create                 # create new branch
obsidian git branch switch                 # switch branch
obsidian git branch delete                 # delete branch
```

### Tasks plugin (requires Tasks plugin)
```bash
# Add task with emoji markers
obsidian tasks add "Fix the bug" --file "AI Workspace/inbox.md"
obsidian tasks add "Review PR" --file "AI Workspace/inbox.md" --due 2026-05-20 --priority high
obsidian tasks add "Weekly review" --file "AI Workspace/inbox.md" --recur "every week"

# List tasks (filesystem scan — no Obsidian needed)
obsidian tasks list                        # all tasks in vault
obsidian tasks list --folder "AI Workspace"       # tasks in folder
obsidian tasks list --open-only            # incomplete only
obsidian tasks list --done-only            # complete only

# Obsidian UI
obsidian tasks ui                          # open Tasks create/edit modal
obsidian tasks toggle                      # toggle done at cursor
```

### Templater plugin (requires Templater plugin)
```bash
obsidian template insert    # open insert template modal
obsidian template create    # create note from template
obsidian template apply     # replace templates in active file
obsidian template jump      # jump to next cursor location
```

### Linter (requires Obsidian Linter plugin)
```bash
obsidian lint               # lint active file
obsidian lint --all         # lint entire vault
obsidian lint --folder      # lint current folder
```

### Obsidian commands
```bash
obsidian commands list                              # list all commands
obsidian commands run editor:open-link-in-new-tab  # run any command
```

### QuickAdd plugin (requires QuickAdd plugin)
```bash
obsidian quickadd                        # open QuickAdd modal
obsidian quickadd list                   # list all configured choices
obsidian quickadd run "Daily Note"       # run a choice by name (case-insensitive)
```

### Refactor tools
```bash
obsidian refactor rename "AI Workspace/old.md" "new-name"                    # rename note
obsidian refactor extract "AI Workspace/note.md" "## Section" "AI Workspace/sec.md" # extract heading to new note
obsidian refactor merge "AI Workspace/a.md" "AI Workspace/b.md" "AI Workspace/merged.md"   # merge notes into one
```

### Auto Note Mover (requires Auto Note Mover plugin)
```bash
obsidian mover rules                     # list configured mover rules
obsidian mover check "AI Workspace/my-note.md" # check which rule would match
obsidian mover move "AI Workspace/my-note.md"  # trigger plugin to move the active note
```

### Metadata Menu (requires Metadata Menu plugin)
```bash
obsidian meta schema Book               # show field schema for a fileClass
obsidian meta get "AI Workspace/note.md" status    # get a frontmatter field value
obsidian meta set "AI Workspace/note.md" status active  # set a frontmatter field value
obsidian meta ui                         # open Metadata Menu field editor
```

### Core Obsidian UI commands
```bash
obsidian core palette           # open command palette
obsidian core search            # open global search
obsidian core settings          # open settings
obsidian core graph             # open graph view
obsidian core new-tab           # open new tab
obsidian core pin               # pin/unpin current tab
obsidian core split horizontal  # split pane horizontally
obsidian core split vertical    # split pane vertically
```

### Periodic notes navigation
```bash
obsidian periodic nav daily prev   # navigate to previous daily note
obsidian periodic nav daily next   # navigate to next daily note
obsidian periodic nav weekly prev  # navigate to previous weekly note
```

## Canvas Color Guide
- `"1"` = red (warnings, problems)
- `"2"` = orange (in progress)
- `"3"` = yellow (pending, todo)
- `"4"` = green (done, success)
- `"5"` = cyan (info, reference)
- `"6"` = purple (important, highlight)

## Output Format

Every command returns JSON. Always parse the output.
- Success: `{"ok": true, ...}` or `{"content": "...", ...}`
- Error: `{"error": true, "message": "..."}`
- Transport used: `"transport": "api"` (REST API) or `"transport": "fs"` (file system fallback)

## Installing This Skill In A Project

Copy `obsidian_skill.md` into your project's root folder. Your AI agent will pick it up automatically as a project-level skill on the next session.
