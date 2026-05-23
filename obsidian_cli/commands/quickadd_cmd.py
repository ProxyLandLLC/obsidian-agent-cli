import json
from pathlib import Path
import click
from ..config import load_config
from ..transport import Transport


def _load_quickadd_config(vault_path: str) -> dict | None:
    config_path = Path(vault_path) / ".obsidian" / "plugins" / "quickadd" / "data.json"
    if not config_path.exists():
        return None
    return json.loads(config_path.read_text(encoding="utf-8"))


def _find_choice(choices: list, name: str) -> dict | None:
    name_lower = name.lower()
    for choice in choices:
        if choice.get("name", "").lower() == name_lower:
            return choice
    return None


@click.group("quickadd", invoke_without_command=True)
@click.pass_context
def quickadd_cmd(ctx):
    """QuickAdd plugin commands (requires QuickAdd plugin).

    Without subcommand: opens the QuickAdd modal.
    """
    if ctx.invoked_subcommand is None:
        cfg = load_config()
        t = Transport(cfg)
        result = t.run_command("quickadd:runQuickAdd")
        click.echo(json.dumps(result))


@quickadd_cmd.command("list")
def list_choices():
    """List all QuickAdd choices configured in the plugin."""
    cfg = load_config()
    qa_config = _load_quickadd_config(cfg.vault_path)
    if qa_config is None:
        click.echo(json.dumps({"error": True,
                               "message": "QuickAdd plugin not found. Is it installed in Obsidian?"}))
        return
    choices = [
        {"id": c.get("id"), "name": c.get("name"), "type": c.get("type")}
        for c in qa_config.get("choices", [])
    ]
    click.echo(json.dumps({"choices": choices, "count": len(choices)}))


@quickadd_cmd.command("run")
@click.argument("name")
def run_choice(name):
    """Run a QuickAdd choice by name."""
    cfg = load_config()
    qa_config = _load_quickadd_config(cfg.vault_path)
    if qa_config is None:
        click.echo(json.dumps({"error": True,
                               "message": "QuickAdd plugin not found. Is it installed in Obsidian?"}))
        return
    choice = _find_choice(qa_config.get("choices", []), name)
    if choice is None:
        available = [c.get("name") for c in qa_config.get("choices", [])]
        click.echo(json.dumps({
            "error": True,
            "message": f"Choice '{name}' not found.",
            "available": available,
        }))
        return
    t = Transport(cfg)
    result = t.run_command(f"quickadd:choice:{choice['id']}")
    if "ok" in result:
        result["choice"] = choice["name"]
    click.echo(json.dumps(result))
