import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote
import click
from ..config import load_config


@click.group()
def uri():
    """Obsidian URI scheme commands (work without REST API running)."""


@uri.command()
@click.option("--name", required=True, help="Note title")
@click.option("--content", default="", help="Initial note content")
@click.option("--folder", default="", help="Vault-relative folder path")
@click.option("--silent", is_flag=True, default=False, help="Create without opening in Obsidian")
@click.option("--append", "do_append", is_flag=True, default=False, help="Append if note exists")
@click.option("--overwrite", is_flag=True, default=False, help="Overwrite if note exists")
def new(name, content, folder, silent, do_append, overwrite):
    """Create a new note via obsidian:// URI scheme."""
    cfg = load_config()
    vault_name = Path(cfg.vault_path).name
    params = f"vault={quote(vault_name)}&name={quote(name)}"
    if content:
        params += f"&content={quote(content)}"
    if folder:
        params += f"&filepath={quote(folder + '/' + name + '.md')}"
    if silent:
        params += "&silent=true"
    if do_append:
        params += "&append=true"
    if overwrite:
        params += "&overwrite=true"
    uri_str = f"obsidian://new?{params}"
    _open_uri(uri_str)
    click.echo(json.dumps({"ok": True, "uri": uri_str, "transport": "uri"}))


@uri.command()
@click.argument("query")
def search(query):
    """Open Obsidian search UI with a pre-filled query."""
    cfg = load_config()
    vault_name = Path(cfg.vault_path).name
    uri_str = f"obsidian://search?vault={quote(vault_name)}&query={quote(query)}"
    _open_uri(uri_str)
    click.echo(json.dumps({"ok": True, "uri": uri_str, "transport": "uri"}))


def _open_uri(uri_str: str) -> None:
    if sys.platform == "win32":
        subprocess.Popen(["cmd", "/c", "start", uri_str], shell=False)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", uri_str])
    else:
        subprocess.Popen(["xdg-open", uri_str])
