import json
import click
from ..config import load_config
from ..transport import Transport


@click.command("status")
def status_cmd():
    """Show Obsidian REST API health, version, and auth status."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.get_server_status()
    click.echo(json.dumps(result))
