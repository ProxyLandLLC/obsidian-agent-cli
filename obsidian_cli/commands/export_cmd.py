import json
from pathlib import Path
from datetime import datetime
import click
from ..config import load_config


@click.group("export")
def export_cmd():
    """Export vault notes to portable formats."""


@export_cmd.command("bundle")
@click.argument("output", default=None, required=False)
@click.option("--folder", default="AI Workspace", help="Vault folder to bundle")
@click.option("--separator", default="\n\n---\n\n", help="Separator between notes")
def export_bundle(output, folder, separator):
    """Concatenate notes into a single markdown file (useful for AI context)."""
    cfg = load_config()
    vault = Path(cfg.vault_path)
    base = vault / folder if folder else vault
    if not base.exists():
        click.echo(json.dumps({"error": True, "message": f"Folder not found: {folder}"}))
        return

    if output is None:
        ts = datetime.now().strftime("%Y%m%d-%H%M%S")
        label = folder.replace("/", "-") or "vault"
        output = str(vault.parent / f"obsidian-bundle-{label}-{ts}.md")

    sections = []
    for p in sorted(base.rglob("*.md")):
        if ".obsidian" in p.parts:
            continue
        rel = str(p.relative_to(vault)).replace("\\", "/")
        content = p.read_text(encoding="utf-8", errors="ignore")
        sections.append(f"<!-- source: {rel} -->\n{content}")

    Path(output).write_text(separator.join(sections), encoding="utf-8")
    click.echo(json.dumps({"ok": True, "output": output, "files": len(sections)}))
