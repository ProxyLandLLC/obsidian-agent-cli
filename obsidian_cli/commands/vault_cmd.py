import json
from pathlib import Path
import click
from ..config import load_config
from ..transport import Transport


@click.group("vault")
def vault_cmd():
    """Vault-level file operations (find, move)."""


@vault_cmd.command("find")
@click.argument("pattern")
@click.option("--folder", default="", help="Limit search to this folder")
def find(pattern, folder):
    """Find notes by glob pattern (e.g. '**/*meeting*.md')."""
    cfg = load_config()
    vault = Path(cfg.vault_path)
    base = vault / folder if folder else vault
    if not base.exists():
        click.echo(json.dumps({"error": True, "message": f"Folder not found: {folder}"}))
        return
    matches = [
        str(p.relative_to(vault)).replace("\\", "/")
        for p in base.glob(pattern)
        if ".obsidian" not in p.parts
    ]
    click.echo(json.dumps({"pattern": pattern, "matches": sorted(matches), "count": len(matches)}))


@vault_cmd.command("move")
@click.argument("src")
@click.argument("dest")
def move(src, dest):
    """Move or rename a note (copies content then deletes source)."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.move_file(src, dest)
    click.echo(json.dumps(result))
