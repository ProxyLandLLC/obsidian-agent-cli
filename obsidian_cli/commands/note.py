import json
import click
from ..config import load_config
from ..transport import Transport

_DQL = "application/vnd.olrapi.dataview.dql+txt"


@click.group()
def note():
    """Note CRUD operations."""


@note.command()
@click.argument("path")
@click.option("--content", default="", help="Initial content")
def create(path, content):
    cfg = load_config()
    t = Transport(cfg)
    result = t.write_file(path, content)
    click.echo(json.dumps(result))


@note.command()
@click.argument("path")
def read(path):
    cfg = load_config()
    t = Transport(cfg)
    result = t.read_file(path)
    click.echo(json.dumps(result))


@note.command()
@click.argument("path")
@click.argument("content")
@click.option("--append", is_flag=True, default=False)
def update(path, content, append):
    cfg = load_config()
    t = Transport(cfg)
    if append:
        existing = t.read_file(path)
        if "error" in existing:
            click.echo(json.dumps(existing))
            return
        content = existing["content"] + "\n" + content
    result = t.write_file(path, content)
    click.echo(json.dumps(result))


@note.command()
@click.argument("path")
@click.argument("content")
@click.option("--operation", default="append", type=click.Choice(["append", "prepend", "replace"]))
@click.option("--target-type", default="heading", type=click.Choice(["heading", "block", "frontmatter"]))
@click.option("--target", required=True, help="Heading name, block ref, or frontmatter key")
@click.option("--create-if-missing", is_flag=True, default=False)
@click.option("--apply-if-preexists", is_flag=True, default=False)
@click.option("--trim-whitespace", is_flag=True, default=False)
def patch(path, content, operation, target_type, target,
          create_if_missing, apply_if_preexists, trim_whitespace):
    cfg = load_config()
    t = Transport(cfg)
    result = t.patch_file(path, content, operation, target_type, target,
                          create_if_missing, apply_if_preexists, trim_whitespace)
    click.echo(json.dumps(result))


@note.command()
@click.argument("path")
def delete(path):
    cfg = load_config()
    t = Transport(cfg)
    result = t.delete_file(path)
    click.echo(json.dumps(result))


@note.command("open")
@click.argument("path")
def open_note(path):
    cfg = load_config()
    t = Transport(cfg)
    result = t.open_in_obsidian(path)
    click.echo(json.dumps(result))


@note.command("list")
@click.argument("folder", default="")
def list_notes(folder):
    cfg = load_config()
    t = Transport(cfg)
    result = t.list_files(folder)
    click.echo(json.dumps(result))


@note.command()
@click.argument("path")
@click.option("--frontmatter", "show_frontmatter", is_flag=True, default=False)
@click.option("--tags", "show_tags", is_flag=True, default=False)
@click.option("--stat", "show_stat", is_flag=True, default=False)
def meta(path, show_frontmatter, show_tags, show_stat):
    """Return parsed frontmatter, tags, and file stats for a note."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.get_note_meta(path)
    if "error" in result:
        click.echo(json.dumps(result))
        return
    if show_frontmatter:
        click.echo(json.dumps({"frontmatter": result.get("frontmatter", {}), "transport": result["transport"]}))
    elif show_tags:
        click.echo(json.dumps({"tags": result.get("tags", []), "transport": result["transport"]}))
    elif show_stat:
        click.echo(json.dumps({"stat": result.get("stat", {}), "transport": result["transport"]}))
    else:
        click.echo(json.dumps(result))


@note.command("map")
@click.argument("path")
def map_note(path):
    """List all headings, blocks, and frontmatter fields in a note (patch targets)."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.get_note_map(path)
    click.echo(json.dumps(result))


@note.command()
@click.argument("path")
def backlinks(path):
    """List notes that link to this note (requires Dataview plugin)."""
    from pathlib import Path as _Path
    cfg = load_config()
    t = Transport(cfg)
    note_name = _Path(path).stem
    result = t.search_advanced(f"LIST FROM [[{note_name}]]", _DQL)
    click.echo(json.dumps(result))


@note.command()
@click.option("--limit", default=10, show_default=True, help="Max results")
def recent(limit):
    """List recently modified notes (requires Dataview plugin)."""
    cfg = load_config()
    t = Transport(cfg)
    dql = f'TABLE file.name, file.mtime FROM "" SORT file.mtime DESC LIMIT {limit}'
    result = t.search_advanced(dql, _DQL)
    click.echo(json.dumps(result))


@note.command("by-tag")
@click.argument("tag")
def by_tag(tag):
    """List notes with a given tag (requires Dataview plugin)."""
    cfg = load_config()
    t = Transport(cfg)
    tag_clean = tag.lstrip("#")
    result = t.search_advanced(f"LIST FROM #{tag_clean}", _DQL)
    click.echo(json.dumps(result))


@note.command()
@click.argument("path")
def links(path):
    """List notes this note links to (requires Dataview plugin)."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.search_advanced(f'LIST file.outlinks FROM "{path}"', _DQL)
    click.echo(json.dumps(result))


@note.command()
def orphans():
    """List notes with no incoming links (requires Dataview plugin)."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.search_advanced('LIST FROM "" WHERE length(file.inlinks) = 0', _DQL)
    click.echo(json.dumps(result))
