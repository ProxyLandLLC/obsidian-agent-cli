# obsidian_skill.md Setup Guide

## What It Is

`obsidian_skill.md` is a project-level skill file for AI coding agents (Claude Code, Codex, Gemini CLI, and others that support skill/context files). When you copy it into a project's root folder, your AI agent automatically loads it at the start of every session and gains:

- **Knowledge** of every `obsidian` CLI command and when to use it
- **Auto-trigger rules** — things the agent does without being asked (recall project context, log discoveries)
- **On-demand rules** — things the agent only does when explicitly asked (write teaching notes, build canvases)

Without `obsidian_skill.md`, your AI agent has no awareness of the CLI. With it, it acts as a persistent knowledge store across every session.

---

## Prerequisites

The `obsidian` CLI must be installed and configured on the machine running your AI agent. See [INSTALL.md](./INSTALL.md).

To verify:
```bash
obsidian status
```

---

## Installing the Skill in a Project

Copy `obsidian_skill.md` from this repo into the root of any project where you want vault integration:

```bash
# macOS / Linux
cp /path/to/obsidian-cli/obsidian_skill.md <your-project-root>/obsidian_skill.md

# Windows (PowerShell)
Copy-Item "C:\path\to\obsidian-cli\obsidian_skill.md" "<your-project-root>\obsidian_skill.md"
```

That's it. Your AI agent picks it up automatically on the next session — no other configuration needed.

---

## What The AI Agent Does Automatically

These happen **without you asking**, every session:

### At the start of a session on a registered project
```bash
obsidian workspace recall <project-name>
```
The agent reads everything it has previously logged about the project before responding to anything else.

### When a new project is encountered for the first time
```bash
obsidian workspace project register <project-name>
```
Registers it in the vault registry so future sessions can recall it.

### After discovering something architecturally significant
```bash
obsidian workspace log <project-name> "Auth uses RS256 JWTs. Token expiry is 15 min."
obsidian workspace log <project-name> "Decision: kept Postgres — team knows it well"
```
Triggered by: design patterns, tech choices, gotchas, key files, decisions made during the session.

---

## What The AI Agent Does Only When Asked

These require an explicit user request:

### "Give me a visual overview of this codebase"
```bash
obsidian canvas build "<project>-overview" --spec '<json spec>'
obsidian canvas open "AI Workspace/<project>/<name>.canvas"
```

### "Explain how X works" / "Teach me about Y"
```bash
obsidian teach write "<Topic Title>" --content "<markdown explanation>"
```

### Bulk operations (tag rename, batch edits, export)
Only when the user asks — never speculatively.

---

## What The AI Agent Does NOT Do

- Log trivial changes (typo fixes, formatting, single-line edits)
- Write teaching notes unless explicitly asked
- Build canvases for small or single-file changes
- Log things already in the knowledge log

---

## Registering a Project (First Session)

On the first session in a new project:

1. Copy `obsidian_skill.md` into the project root.
2. Start an AI agent session.
3. The agent will automatically run:
   ```bash
   obsidian workspace project register <project-name>
   ```
4. From that point on, every session starts with a `recall` — the agent always knows what it learned before.

---

## Keeping the Skill Up to Date

When the CLI gains new commands, `obsidian_skill.md` is updated in this repo. To update a project's skill, copy the new version into the project root (replacing the old one). The agent will pick up the updated version on the next session.

---

## How The Auto-Trigger Works (Internals)

AI agents load `obsidian_skill.md` found in the project root at session start. The frontmatter at the top of the file defines the trigger conditions:

```yaml
---
name: obsidian-vault
description: Use when working on any software project — manages knowledge capture...
triggers:
  - starting work on a project
  - discovering architectural decisions
  - user asks for visual overview
  - user asks for explanation of something
---
```

The agent matches these triggers against what's happening in the session and invokes the skill accordingly.
