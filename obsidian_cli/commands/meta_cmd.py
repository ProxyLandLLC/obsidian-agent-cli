import json
import re
from pathlib import Path
import click
from ..config import load_config
from ..transport import Transport


def _parse_fields_from_fileclass(content: str) -> list[dict]:
    fields = []
    current = {}
    for line in content.splitlines():
        m = re.match(r"^- name:\s*(.+)$", line.strip())
        if m:
            if current:
                fields.append(current)
            current = {"name": m.group(1).strip()}
            continue
        m = re.match(r"^\s+type:\s*(.+)$", line)
        if m and current:
            current["type"] = m.group(1).strip()
            continue
        m = re.match(r"^\s+required:\s*(.+)$", line)
        if m and current:
            current["required"] = m.group(1).strip().lower() == "true"
            continue
        m = re.match(r"^\s+options:\s*\[(.+)\]$", line)
        if m and current:
            current["options"] = [o.strip().strip("'\"") for o in m.group(1).split(",")]
    if current:
        fields.append(current)
    return fields


def _load_fileclass_fields(vault_path: str, fileclass: str) -> list[dict] | None:
    note_path = Path(vault_path) / "_fileClass" / f"{fileclass}.md"
    if not note_path.exists():
        return None
    content = note_path.read_text(encoding="utf-8")
    return _parse_fields_from_fileclass(content)


@click.group("meta")
def meta_cmd():
    """Metadata Menu plugin commands (frontmatter fields)."""


@meta_cmd.command("schema")
@click.argument("fileclass")
def get_schema(fileclass):
    """Show field schema for a fileClass."""
    cfg = load_config()
    fields = _load_fileclass_fields(cfg.vault_path, fileclass)
    if fields is None:
        click.echo(json.dumps({"error": True, "message": f"fileClass '{fileclass}' not found in _fileClass/ folder."}))
        return
    click.echo(json.dumps({"fileclass": fileclass, "fields": fields, "count": len(fields)}))


@meta_cmd.command("get")
@click.argument("note_path")
@click.argument("field")
def get_field(note_path, field):
    """Get a frontmatter field value from a note."""
    cfg = load_config()
    t = Transport(cfg)
    meta = t.get_note_meta(note_path)
    if "error" in meta and meta["error"]:
        click.echo(json.dumps(meta))
        return
    frontmatter = meta.get("frontmatter", {})
    if field not in frontmatter:
        click.echo(json.dumps({"error": True, "message": f"Field '{field}' not found in frontmatter.", "note": note_path}))
        return
    click.echo(json.dumps({"note": note_path, "field": field, "value": frontmatter[field]}))


@meta_cmd.command("set")
@click.argument("note_path")
@click.argument("field")
@click.argument("value")
def set_field(note_path, field, value):
    """Set a frontmatter field value in a note."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.patch_file(note_path, value, "replace", "frontmatter", field,
                          True, False, False)
    click.echo(json.dumps({**result, "note": note_path, "field": field, "value": value}))


@meta_cmd.command("ui")
def open_ui():
    """Open the Metadata Menu field editor UI."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("metadata-menu:open-field-manager")
    click.echo(json.dumps(result))
