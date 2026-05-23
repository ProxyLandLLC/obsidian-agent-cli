import json
import click
from ..config import load_config, save_config, Config


@click.group("config")
def config_cmd():
    """View and update CLI configuration."""


@config_cmd.command()
def show():
    cfg = load_config()
    data = {
        "vault_path": cfg.vault_path,
        "workspace_path": cfg.workspace_path,
        "teach_path": cfg.teach_path,
        "api_url": cfg.api_url,
        "api_key": "***" if cfg.api_key else "(not set)",
        "api_verify_ssl": cfg.api_verify_ssl,
    }
    click.echo(json.dumps(data, indent=2))


@config_cmd.command()
@click.argument("key")
@click.argument("value")
def set(key, value):
    cfg = load_config()
    if not hasattr(cfg, key):
        click.echo(json.dumps({"error": True, "message": f"Unknown key: {key}"}))
        return
    field_type = type(getattr(cfg, key))
    if field_type == bool:
        value = value.lower() in ("true", "1", "yes")
    if key == "api_key":
        click.echo("Warning: api_key set via CLI is visible in shell history. Use obsidian config init instead.", err=True)
    setattr(cfg, key, value)
    save_config(cfg)
    click.echo(json.dumps({"ok": True, "key": key}))


@config_cmd.command()
def init():
    """Interactive first-time setup."""
    click.echo("Obsidian CLI Setup")
    click.echo("------------------")
    vault = click.prompt("Vault path (full path to your Obsidian vault folder)").lstrip("﻿")
    api_key = click.prompt("API key (from Obsidian Local REST API plugin settings)", default="").lstrip("﻿")
    api_url = click.prompt("API URL", default="http://127.0.0.1:27123").lstrip("﻿")
    cfg = Config(
        vault_path=vault,
        api_url=api_url,
        api_key=api_key,
    )
    save_config(cfg)
    click.echo(json.dumps({"ok": True, "message": "Config saved. Run: obsidian config show"}))
