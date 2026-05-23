import json
import click
from ..config import load_config
from ..transport import Transport


@click.group()
def commands():
    """List and execute Obsidian commands."""


@commands.command("list")
def list_commands():
    cfg = load_config()
    t = Transport(cfg)
    result = t.list_commands()
    click.echo(json.dumps(result))


@commands.command("run")
@click.argument("command_id")
def run_command(command_id):
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command(command_id)
    click.echo(json.dumps(result))
