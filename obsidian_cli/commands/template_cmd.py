import json
import click
from ..config import load_config
from ..transport import Transport


@click.group("template")
def template_cmd():
    """Templater plugin commands (requires Templater plugin)."""


@template_cmd.command()
def insert():
    """Open the insert template modal in Obsidian."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("templater-obsidian:insert-templater")
    click.echo(json.dumps(result))


@template_cmd.command()
def create():
    """Create a new note from a template (opens Obsidian modal to pick template)."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("templater-obsidian:create-new-note-from-template")
    click.echo(json.dumps(result))


@template_cmd.command()
def apply():
    """Replace all template placeholders in the active file."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("templater-obsidian:replace-in-file-templater")
    click.echo(json.dumps(result))


@template_cmd.command()
def jump():
    """Jump to the next cursor location in a template."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("templater-obsidian:jump-to-next-cursor-location")
    click.echo(json.dumps(result))
