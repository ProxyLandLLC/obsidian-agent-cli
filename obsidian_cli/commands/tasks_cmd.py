import json
import re
from datetime import date
from pathlib import Path
import click
from ..config import load_config
from ..transport import Transport

_PRIORITY_EMOJI = {
    "highest": "⏫",
    "high": "🔼",
    "medium": "🔳",
    "low": "🔽",
    "lowest": "⏬",
}

_CREATED_EMOJI = "➕"
_DUE_EMOJI = "📅"
_SCHEDULED_EMOJI = "⏳"
_START_EMOJI = "🛫"
_RECUR_EMOJI = "🔁"


def _build_task_line(description: str, priority: str = "",
                     due: str = "", scheduled: str = "",
                     start: str = "", recur: str = "") -> str:
    parts = [description]
    if priority and priority in _PRIORITY_EMOJI:
        parts.append(_PRIORITY_EMOJI[priority])
    if due:
        parts.append(f"{_DUE_EMOJI} {due}")
    if scheduled:
        parts.append(f"{_SCHEDULED_EMOJI} {scheduled}")
    if start:
        parts.append(f"{_START_EMOJI} {start}")
    if recur:
        parts.append(f"{_RECUR_EMOJI} {recur}")
    parts.append(f"{_CREATED_EMOJI} {date.today().isoformat()}")
    return "- [ ] " + " ".join(parts)


def _parse_tasks_from_content(content: str, file_path: str) -> list[dict]:
    tasks = []
    for line in content.splitlines():
        todo = re.match(r"^- \[ \] (.+)$", line)
        done = re.match(r"^- \[x\] (.+)$", line, re.IGNORECASE)
        if todo:
            tasks.append({"text": todo.group(1).strip(), "done": False, "file": file_path})
        elif done:
            tasks.append({"text": done.group(1).strip(), "done": True, "file": file_path})
    return tasks


@click.group("tasks")
def tasks_cmd():
    """Tasks plugin integration (requires Tasks plugin)."""


@tasks_cmd.command()
@click.argument("description")
@click.option("--file", "file_path", required=True, help="Vault-relative path to append task to")
@click.option("--priority", default="",
              type=click.Choice(["", "highest", "high", "medium", "low", "lowest"]),
              help="Task priority")
@click.option("--due", default="", help="Due date (YYYY-MM-DD)")
@click.option("--scheduled", default="", help="Scheduled date (YYYY-MM-DD)")
@click.option("--start", default="", help="Start date (YYYY-MM-DD)")
@click.option("--recur", default="", help="Recurrence rule (e.g. 'every week')")
def add(description, file_path, priority, due, scheduled, start, recur):
    """Add a task to a note file."""
    cfg = load_config()
    t = Transport(cfg)
    task_line = _build_task_line(description, priority=priority, due=due,
                                  scheduled=scheduled, start=start, recur=recur)
    raw = t.read_file(file_path)
    if "error" in raw:
        existing = ""
    else:
        existing = raw["content"].rstrip()
    new_content = existing + "\n" + task_line + "\n" if existing else task_line + "\n"
    result = t.write_file(file_path, new_content)
    if "ok" in result:
        result["task"] = task_line
    click.echo(json.dumps(result))


@tasks_cmd.command("list")
@click.option("--folder", default="", help="Vault-relative folder to search (default: entire vault)")
@click.option("--open-only", is_flag=True, default=False, help="Show only incomplete tasks")
@click.option("--done-only", is_flag=True, default=False, help="Show only completed tasks")
def list_tasks(folder, open_only, done_only):
    """List tasks found in vault files (filesystem scan)."""
    cfg = load_config()
    root = Path(cfg.vault_path) / folder if folder else Path(cfg.vault_path)
    all_tasks = []
    for md_file in root.rglob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
        except Exception:
            continue
        rel_path = str(md_file.relative_to(cfg.vault_path)).replace("\\", "/")
        all_tasks.extend(_parse_tasks_from_content(content, rel_path))
    if open_only:
        all_tasks = [t for t in all_tasks if not t["done"]]
    elif done_only:
        all_tasks = [t for t in all_tasks if t["done"]]
    click.echo(json.dumps({"tasks": all_tasks, "count": len(all_tasks), "transport": "fs"}))


@tasks_cmd.command()
def ui():
    """Open the Tasks create-or-edit modal in Obsidian."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("obsidian-tasks-plugin:create-or-edit-task")
    click.echo(json.dumps(result))


@tasks_cmd.command()
def toggle():
    """Toggle the done state of the task at the active cursor."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("obsidian-tasks-plugin:toggle-done")
    click.echo(json.dumps(result))
