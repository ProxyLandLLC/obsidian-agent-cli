import json
import re
from pathlib import Path
import click
from ..config import load_config
from ..transport import Transport


def _iter_notes(vault_path: str, folder: str = "", pattern: str = "**/*.md") -> list[str]:
    vault = Path(vault_path)
    base = vault / folder if folder else vault
    return [
        str(p.relative_to(vault)).replace("\\", "/")
        for p in base.glob(pattern)
        if ".obsidian" not in p.parts
    ]


@click.group("batch")
def batch_cmd():
    """Bulk operations across multiple notes."""


@batch_cmd.command("frontmatter")
@click.argument("field")
@click.argument("value")
@click.option("--folder", default="", help="Limit to this vault folder")
@click.option("--pattern", default="**/*.md", help="Glob pattern for notes")
@click.option("--dry-run", is_flag=True, default=False)
def batch_frontmatter(field, value, folder, pattern, dry_run):
    """Set a frontmatter field to VALUE in all matching notes."""
    cfg = load_config()
    t = Transport(cfg)
    notes = _iter_notes(cfg.vault_path, folder, pattern)
    changed = []
    errors = []
    for note_path in notes:
        if dry_run:
            changed.append(note_path)
            continue
        result = t.patch_file(note_path, value, "replace", "frontmatter", field,
                              True, False, False)
        if result.get("error"):
            errors.append({"note": note_path, "message": result.get("message")})
        else:
            changed.append(note_path)
    click.echo(json.dumps({
        "field": field, "value": value,
        "changed_count": len(changed), "changed": changed,
        "error_count": len(errors), "errors": errors,
        "dry_run": dry_run,
    }))


@batch_cmd.command("rename")
@click.argument("search")
@click.argument("replacement")
@click.option("--folder", default="", help="Limit to this vault folder")
@click.option("--pattern", default="**/*.md")
@click.option("--regex", "use_regex", is_flag=True, default=False, help="Treat SEARCH as regex")
@click.option("--dry-run", is_flag=True, default=False)
def batch_rename(search, replacement, folder, pattern, use_regex, dry_run):
    """Find-and-replace text across note contents."""
    cfg = load_config()
    vault = Path(cfg.vault_path)
    notes = _iter_notes(cfg.vault_path, folder, pattern)
    changed = []
    skipped = []
    re_search = re.compile(search) if use_regex else None
    for rel in notes:
        p = vault / rel
        text = p.read_text(encoding="utf-8", errors="ignore")
        if use_regex:
            if not re_search.search(text):
                skipped.append(rel)
                continue
            new_text = re_search.sub(replacement, text)
        else:
            if search not in text:
                skipped.append(rel)
                continue
            new_text = text.replace(search, replacement)
        changed.append(rel)
        if not dry_run:
            p.write_text(new_text, encoding="utf-8")
    click.echo(json.dumps({
        "search": search, "replacement": replacement,
        "changed_count": len(changed), "changed": changed,
        "skipped_count": len(skipped),
        "dry_run": dry_run,
    }))
