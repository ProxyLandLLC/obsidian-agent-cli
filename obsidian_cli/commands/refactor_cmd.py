import json
import click
from ..config import load_config
from ..transport import Transport


@click.group("refactor")
def refactor_cmd():
    """Note refactoring tools (rename, extract, merge)."""


@refactor_cmd.command("rename")
@click.argument("old_path")
@click.argument("new_name")
def rename_note(old_path, new_name):
    """Rename a note (update title + filename via URI)."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command(f"obsidian-file-path-rename:rename-file")
    click.echo(json.dumps({**result, "old_path": old_path, "new_name": new_name}))


@refactor_cmd.command("extract")
@click.argument("source_path")
@click.argument("heading")
@click.argument("dest_path")
def extract_heading(source_path, heading, dest_path):
    """Extract a heading section from a note into a new note."""
    cfg = load_config()
    t = Transport(cfg)
    source = t.get_note(source_path)
    if "content" not in source:
        click.echo(json.dumps(source))
        return

    lines = source["content"].splitlines(keepends=True)
    heading_prefix = heading.lstrip("#").strip()
    level = len(heading) - len(heading.lstrip("#"))
    if level == 0:
        level = 1
        heading_prefix = heading.strip()

    start = None
    end = None
    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if start is None:
            if stripped.startswith("#" * level + " ") and stripped[level + 1:].strip() == heading_prefix:
                start = i
        elif start is not None:
            if stripped.startswith("#") and len(stripped) - len(stripped.lstrip("#")) <= level and i != start:
                end = i
                break

    if start is None:
        click.echo(json.dumps({"error": True, "message": f"Heading '{heading}' not found in {source_path}"}))
        return

    section_lines = lines[start:end]
    section = "".join(section_lines)
    result = t.create_note(dest_path, section)
    click.echo(json.dumps({**result, "extracted_heading": heading_prefix, "dest": dest_path}))


@refactor_cmd.command("merge")
@click.argument("paths", nargs=-1, required=True)
@click.argument("dest_path")
def merge_notes(paths, dest_path):
    """Merge multiple notes into one (append in order)."""
    cfg = load_config()
    t = Transport(cfg)
    combined = []
    for p in paths:
        r = t.get_note(p)
        if "content" not in r:
            click.echo(json.dumps({**r, "failed_path": p}))
            return
        combined.append(r["content"])
    merged = "\n\n---\n\n".join(combined)
    result = t.create_note(dest_path, merged)
    click.echo(json.dumps({**result, "merged_count": len(paths), "dest": dest_path}))
