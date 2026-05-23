import json
from datetime import datetime
import click
from ..config import load_config
from ..transport import Transport

_PERIODS = click.Choice(["daily", "weekly", "monthly", "quarterly", "yearly"])


@click.group()
def periodic():
    """Periodic notes (daily, weekly, etc.)."""


@periodic.command()
def today():
    cfg = load_config()
    t = Transport(cfg)
    result = t.get_periodic("daily")
    click.echo(json.dumps(result))


@periodic.command("read-today")
def read_today():
    cfg = load_config()
    t = Transport(cfg)
    result = t.get_periodic("daily")
    click.echo(json.dumps(result))


@periodic.command()
@click.argument("period", type=_PERIODS)
def get(period):
    cfg = load_config()
    t = Transport(cfg)
    result = t.get_periodic(period)
    click.echo(json.dumps(result))


@periodic.command()
@click.argument("period", type=_PERIODS)
@click.argument("content")
def write(period, content):
    """Overwrite the current periodic note."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.write_periodic(period, content)
    click.echo(json.dumps(result))


@periodic.command("append")
@click.argument("period", type=_PERIODS)
@click.argument("content")
def append_cmd(period, content):
    """Append content to the current periodic note."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.append_periodic(period, content)
    click.echo(json.dumps(result))


@periodic.command("patch")
@click.argument("period", type=_PERIODS)
@click.argument("content")
@click.option("--operation", default="append", type=click.Choice(["append", "prepend", "replace"]))
@click.option("--target-type", default="heading", type=click.Choice(["heading", "block", "frontmatter"]))
@click.option("--target", required=True)
@click.option("--create-if-missing", is_flag=True, default=False)
@click.option("--apply-if-preexists", is_flag=True, default=False)
@click.option("--trim-whitespace", is_flag=True, default=False)
def patch_cmd(period, content, operation, target_type, target,
              create_if_missing, apply_if_preexists, trim_whitespace):
    """Patch a section of the current periodic note."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.patch_periodic(period, content, operation, target_type, target,
                              create_if_missing, apply_if_preexists, trim_whitespace)
    click.echo(json.dumps(result))


@periodic.command("delete")
@click.argument("period", type=_PERIODS)
def delete_cmd(period):
    """Delete the current periodic note."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.delete_periodic(period)
    click.echo(json.dumps(result))


@periodic.command("date")
@click.argument("period", type=_PERIODS)
@click.argument("date_str", metavar="DATE")
@click.option("--write", "write_content", default=None, help="Overwrite with content")
@click.option("--append", "append_content", default=None, help="Append content")
@click.option("--delete", "do_delete", is_flag=True, default=False, help="Delete the note")
def periodic_date(period, date_str, write_content, append_content, do_delete):
    """Read/write/delete a specific date's periodic note. DATE format: YYYY-MM-DD."""
    cfg = load_config()
    t = Transport(cfg)
    try:
        d = datetime.strptime(date_str, "%Y-%m-%d")
    except ValueError:
        click.echo(json.dumps({"error": True, "message": f"Invalid date: {date_str}. Use YYYY-MM-DD"}))
        return
    y, m, day = d.year, d.month, d.day
    if do_delete:
        result = t.delete_periodic_date(period, y, m, day)
    elif write_content is not None:
        result = t.write_periodic_date(period, y, m, day, write_content)
    elif append_content is not None:
        result = t.append_periodic_date(period, y, m, day, append_content)
    else:
        result = t.get_periodic_date(period, y, m, day)
    click.echo(json.dumps(result))


@periodic.command("nav")
@click.argument("period", type=_PERIODS)
@click.argument("direction", type=click.Choice(["prev", "next"]))
def nav_cmd(period, direction):
    """Navigate to the previous or next periodic note in Obsidian."""
    cfg = load_config()
    t = Transport(cfg)
    command_id = f"periodic-notes:{direction}-{period}"
    result = t.run_command(command_id)
    click.echo(json.dumps(result))
