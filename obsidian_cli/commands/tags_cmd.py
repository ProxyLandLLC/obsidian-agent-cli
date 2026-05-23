import json
import click
from ..config import load_config
from ..transport import Transport


@click.group("tags")
def tags_cmd():
    """Tag management — rename tags across the vault."""


@tags_cmd.command("rename")
@click.argument("old_tag")
@click.argument("new_tag")
@click.option("--dry-run", is_flag=True, default=False,
              help="Show what would change without modifying files")
def rename_tag(old_tag, new_tag, dry_run):
    """Rename a tag across all vault notes."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.rename_tag_in_vault(old_tag, new_tag, dry_run=dry_run)
    click.echo(json.dumps(result))
