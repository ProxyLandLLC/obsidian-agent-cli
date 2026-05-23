# obsidian-agent-cli Skill

This skill gives your AI agent access to the user's Obsidian vault as a persistent knowledge store via the `obsidian` CLI.

The `obsidian` CLI must be installed (`pip install obsidian-agent-cli`) and configured (`obsidian config init`). All commands output JSON.

Before using any command, check connection:
```bash
obsidian status
```

## Vault Layout

The default workspace layout (configurable via `obsidian config set workspace_path`):

- Workspace folder: `AI Workspace/`
- Teaching notes: `AI Workspace/Teaching Notes/`
- Per-project folders: `AI Workspace/<project-name>/`
- Registry: `AI Workspace/registry.json`

## When To Use

### Auto-trigger (do without being asked):

**At session start on a known project:**
```bash
obsidian workspace recall <project-name>
```

**First time on a new project:**
```bash
obsidian workspace project register <project-name>
```

**After discovering something architecturally significant:**
```bash
obsidian workspace log <project-name> "<discovery>"
obsidian workspace log <project-name> "Decision: <decision and reason>"
```

### On-demand only:

**User asks for an explanation:**
```bash
obsidian teach write "<Topic Title>" --content "<markdown explanation>"
```

**User asks for a visual overview:**
```bash
obsidian canvas build "<project>-overview" --spec '<json spec>'
obsidian canvas open "AI Workspace/<project>/<name>.canvas"
```

## Do NOT Use For

- Trivial changes (typo fixes, single-line edits)
- Teaching notes unless explicitly asked
- Canvases for small or single-file changes
- Logging things already in the knowledge log

## Command Reference

### Knowledge capture
```bash
obsidian workspace project register my-project
obsidian workspace recall my-project
obsidian workspace log my-project "Discovery text"
obsidian workspace status
```

### Notes
```bash
obsidian note create "AI Workspace/my-project/arch.md" --content "# Architecture"
obsidian note read "AI Workspace/my-project/arch.md"
obsidian note update "AI Workspace/my-project/arch.md" "New content" --append
obsidian note patch "AI Workspace/my-project/arch.md" "New line" \
  --operation append --target-type heading --target "Dependencies"
obsidian note list "AI Workspace/my-project"
obsidian note open "AI Workspace/my-project/arch.md"
obsidian note meta "AI Workspace/my-project/arch.md"
obsidian note map "AI Workspace/my-project/arch.md"
obsidian note backlinks "AI Workspace/my-project/arch.md"
obsidian note recent --limit 20
obsidian note by-tag "#project"
```

### Search
```bash
obsidian search simple "authentication"
obsidian search advanced "TABLE file.mtime FROM \"AI Workspace\" SORT file.mtime DESC LIMIT 10"
obsidian search tags
```

### Canvases
```bash
obsidian canvas build "my-project-overview" --spec '{
  "nodes": [
    {"type": "text", "text": "# My Project"},
    {"type": "file", "file": "AI Workspace/my-project/arch.md"}
  ],
  "edges": [{"from": 0, "to": 1, "label": "documented in", "color": "4"}]
}'
obsidian canvas open "AI Workspace/my-project/my-project-overview.canvas"
obsidian canvas add-node "AI Workspace/my-project/overview.canvas" --type file --file "AI Workspace/my-project/new-note.md"
obsidian canvas read "AI Workspace/my-project/overview.canvas"
```

### Teaching notes
```bash
obsidian teach write "How JWT Works" --content "JWT (JSON Web Token) is..."
obsidian teach list
obsidian teach open "How JWT Works"
```

### Active note
```bash
obsidian active read
obsidian active meta
obsidian active write "# New"
obsidian active append "- item"
obsidian active patch "done" --target "Status" --target-type frontmatter --operation replace
obsidian active delete
```

### Periodic notes
```bash
obsidian periodic today
obsidian periodic get weekly
obsidian periodic write daily "# Today\n\nContent"
obsidian periodic append daily "- new item"
obsidian periodic patch daily "done" --target "Tasks" --operation replace
obsidian periodic delete daily
obsidian periodic date daily 2026-05-11
obsidian periodic nav daily prev
obsidian periodic nav daily next
```

### Vault operations
```bash
obsidian vault find "**/*meeting*.md"
obsidian vault find "*.md" --folder "AI Workspace"
obsidian vault move "AI Workspace/old.md" "AI Workspace/new.md"
```

### Tags
```bash
obsidian tags rename "#todo" "#task" --dry-run
obsidian tags rename "#todo" "#task"
```

### Batch operations
```bash
obsidian batch frontmatter status active --folder "AI Workspace" --dry-run
obsidian batch frontmatter status active --folder "AI Workspace"
obsidian batch rename "Old Name" "New Name" --folder "AI Workspace" --dry-run
obsidian batch rename "Old Name" "New Name" --folder "AI Workspace"
obsidian batch rename "\d{4}-\d{2}-\d{2}" "REDACTED" --folder "AI Workspace" --regex
```

### Export
```bash
obsidian export bundle context.md --folder "AI Workspace/my-app"
```

### URI scheme
```bash
obsidian uri new --name "My Note" --folder "AI Workspace/inbox"
obsidian uri search "#project status:active"
```

### Excalidraw
```bash
obsidian excalidraw create "AI Workspace/my-project/diagram.excalidraw"
obsidian excalidraw build "AI Workspace/my-project/flow.excalidraw" --spec '{
  "elements": [
    {"type": "rectangle", "label": "Start"},
    {"type": "ellipse", "label": "Process"}
  ],
  "arrows": [{"from": 0, "to": 1}]
}'
obsidian excalidraw add-shape "AI Workspace/diagram.excalidraw" --type rectangle --label "Box"
obsidian excalidraw add-arrow "AI Workspace/diagram.excalidraw" <from_id> <to_id>
obsidian excalidraw read "AI Workspace/diagram.excalidraw"
obsidian excalidraw open "AI Workspace/diagram.excalidraw"
```

### Kanban
```bash
obsidian kanban create "AI Workspace/my-project/board.md" --lanes "To Do,In Progress,Done"
obsidian kanban read "AI Workspace/my-project/board.md"
obsidian kanban card add "AI Workspace/my-project/board.md" "To Do" "Implement feature X"
obsidian kanban lane add "AI Workspace/my-project/board.md" "Blocked"
obsidian kanban archive "AI Workspace/my-project/board.md"
```

### Git (requires Obsidian Git plugin)
```bash
obsidian git sync
obsidian git sync -m "feat: update notes"
obsidian git commit
obsidian git pull
obsidian git push
obsidian git status
obsidian git fetch
```

### Tasks (requires Tasks plugin)
```bash
obsidian tasks add "Fix the bug" --file "AI Workspace/inbox.md"
obsidian tasks add "Review PR" --file "AI Workspace/inbox.md" --due 2026-05-20 --priority high
obsidian tasks list
obsidian tasks list --folder "AI Workspace" --open-only
```

### Other plugins
```bash
obsidian template insert
obsidian lint
obsidian lint --all
obsidian quickadd run "Daily Note"
obsidian refactor rename "AI Workspace/old.md" "new-name"
obsidian mover rules
obsidian meta get "AI Workspace/note.md" status
obsidian meta set "AI Workspace/note.md" status active
obsidian core palette
obsidian core graph
obsidian commands list
obsidian commands run editor:open-link-in-new-tab
```

### Status & config
```bash
obsidian status
obsidian config show
obsidian config set vault_path /path/to/vault
obsidian config set api_key YOUR_KEY
```

## Canvas Color Guide
- `"1"` = red (warnings)  `"2"` = orange (in progress)  `"3"` = yellow (todo)
- `"4"` = green (done)    `"5"` = cyan (info)            `"6"` = purple (important)

## Output Format

All commands return JSON:
- Success: `{"ok": true, ...}` or `{"content": "...", ...}`
- Error: `{"error": true, "message": "..."}`
- Transport: `"transport": "api"` (REST) or `"transport": "fs"` (filesystem fallback)
