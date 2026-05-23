import json
import click
from ..config import load_config
from ..transport import Transport


@click.group("core")
def core_cmd():
    """Core Obsidian commands (open, search, settings, command palette)."""


@core_cmd.command("open")
@click.argument("note_path")
def open_note(note_path):
    """Open a note in the Obsidian UI."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command(f"app:open-file:{note_path}")
    click.echo(json.dumps({**result, "note": note_path}))


@core_cmd.command("palette")
def command_palette():
    """Open the Obsidian command palette."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("command-palette:open")
    click.echo(json.dumps(result))


@core_cmd.command("search")
def open_search():
    """Open Obsidian global search."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("global-search:open")
    click.echo(json.dumps(result))


@core_cmd.command("settings")
def open_settings():
    """Open Obsidian settings."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("app:open-settings")
    click.echo(json.dumps(result))


@core_cmd.command("graph")
def open_graph():
    """Open Obsidian graph view."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("graph:open")
    click.echo(json.dumps(result))


@core_cmd.command("new-tab")
def new_tab():
    """Open a new tab in Obsidian."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("workspace:new-tab")
    click.echo(json.dumps(result))


@core_cmd.command("pin")
def pin_tab():
    """Pin/unpin the current tab."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("workspace:toggle-pin")
    click.echo(json.dumps(result))


@core_cmd.command("split")
@click.argument("direction", type=click.Choice(["horizontal", "vertical"]))
def split_view(direction):
    """Split the current pane horizontally or vertically."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command(f"workspace:split-{direction}")
    click.echo(json.dumps(result))
