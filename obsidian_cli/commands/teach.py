import json
import re
import click
from ..config import load_config
from ..transport import Transport


@click.group()
def teach():
    """Write teaching/reference notes into your vault."""


@teach.command()
@click.argument("title")
@click.option("--content", required=True, help="Note content (markdown)")
def write(title, content):
    cfg = load_config()
    slug = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "-").lower()
    vault_path = f"{cfg.teach_path}/{slug}.md"
    full_content = f"# {title}\n\n{content}"
    t = Transport(cfg)
    result = t.write_file(vault_path, full_content)
    result["path"] = vault_path
    click.echo(json.dumps(result))


@teach.command("list")
def list_notes():
    cfg = load_config()
    t = Transport(cfg)
    result = t.list_files(cfg.teach_path)
    click.echo(json.dumps(result))


@teach.command("open")
@click.argument("title")
def open_note(title):
    cfg = load_config()
    slug = re.sub(r"[^\w\s-]", "", title).strip().replace(" ", "-").lower()
    vault_path = f"{cfg.teach_path}/{slug}.md"
    t = Transport(cfg)
    result = t.open_in_obsidian(vault_path)
    click.echo(json.dumps(result))
