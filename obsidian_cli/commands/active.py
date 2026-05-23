import json
import click
from ..config import load_config
from ..transport import Transport


@click.group()
def active():
    """Operations on the currently active note in Obsidian."""


@active.command()
def read():
    """Read content of the active note."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.get_active()
    click.echo(json.dumps(result))


@active.command()
def meta():
    """Read frontmatter, tags, and stat of the active note."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.get_active_meta()
    click.echo(json.dumps(result))


@active.command()
@click.argument("content")
def write(content):
    """Overwrite the active note."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.write_active(content)
    click.echo(json.dumps(result))


@active.command("append")
@click.argument("content")
def append_cmd(content):
    """Append content to the active note."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.append_active(content)
    click.echo(json.dumps(result))


@active.command("patch")
@click.argument("content")
@click.option("--operation", default="append", type=click.Choice(["append", "prepend", "replace"]))
@click.option("--target-type", default="heading", type=click.Choice(["heading", "block", "frontmatter"]))
@click.option("--target", required=True)
@click.option("--create-if-missing", is_flag=True, default=False)
@click.option("--apply-if-preexists", is_flag=True, default=False)
@click.option("--trim-whitespace", is_flag=True, default=False)
def patch_cmd(content, operation, target_type, target,
              create_if_missing, apply_if_preexists, trim_whitespace):
    """Patch a section of the active note."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.patch_active(content, operation, target_type, target,
                            create_if_missing, apply_if_preexists, trim_whitespace)
    click.echo(json.dumps(result))


@active.command()
def delete():
    """Delete the active note."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.delete_active()
    click.echo(json.dumps(result))
