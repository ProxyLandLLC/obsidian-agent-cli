import json
import re
from pathlib import Path
import click
from ..config import load_config
from ..transport import Transport


def _load_mover_rules(vault_path: str) -> list:
    config_path = Path(vault_path) / ".obsidian" / "plugins" / "auto-note-mover" / "data.json"
    if not config_path.exists():
        return []
    data = json.loads(config_path.read_text(encoding="utf-8"))
    return data.get("rules", [])


def _match_rule(rules: list, note_name: str, tags: list[str]) -> dict | None:
    for rule in rules:
        pattern = rule.get("pattern", "")
        if not pattern:
            continue
        if pattern.startswith("#"):
            tag = pattern.lstrip("#")
            if any(t.lstrip("#") == tag for t in tags):
                return rule
        else:
            try:
                if re.search(pattern, note_name):
                    return rule
            except re.error:
                pass
    return None


@click.group("mover")
def mover_cmd():
    """Auto Note Mover plugin commands."""


@mover_cmd.command("rules")
def list_rules():
    """List configured Auto Note Mover rules."""
    cfg = load_config()
    rules = _load_mover_rules(cfg.vault_path)
    click.echo(json.dumps({"rules": rules, "count": len(rules)}))


@mover_cmd.command("check")
@click.argument("note_path")
def check_note(note_path):
    """Check which rule (if any) would match a note."""
    cfg = load_config()
    rules = _load_mover_rules(cfg.vault_path)
    if not rules:
        click.echo(json.dumps({"error": True, "message": "Auto Note Mover plugin not found or no rules configured."}))
        return
    t = Transport(cfg)
    meta = t.get_note_meta(note_path)
    if "error" in meta and meta["error"]:
        click.echo(json.dumps(meta))
        return
    note_name = Path(note_path).stem
    tags = meta.get("tags", [])
    rule = _match_rule(rules, note_name, tags)
    if rule is None:
        click.echo(json.dumps({"matched": False, "note": note_path}))
    else:
        click.echo(json.dumps({"matched": True, "note": note_path, "folder": rule.get("folder"), "rule": rule}))


@mover_cmd.command("move")
@click.argument("note_path")
def move_note(note_path):
    """Trigger Auto Note Mover to move a note via plugin command."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("auto-note-mover:move-file")
    click.echo(json.dumps({**result, "note": note_path}))
