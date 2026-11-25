import json
from dataclasses import fields
import click
from ..config import load_config, save_config, Config, FOLDER_FIELDS


@click.group("config")
def config_cmd():
    """View and update CLI configuration."""


@config_cmd.command()
def show():
    cfg = load_config()
    data = {f.name: getattr(cfg, f.name) for f in fields(Config)}
    data["api_key"] = "***" if cfg.api_key else "(not set)"
    for key in ("raw_path", "inbox_path", "projects_path", "reference_path"):
        data[key] = getattr(cfg, key)
    click.echo(json.dumps(data, indent=2))


@config_cmd.command()
@click.argument("key")
@click.argument("value")
def set(key, value):
    cfg = load_config()
    if key not in {f.name for f in fields(Config)}:
        raise click.ClickException(f"Unknown key: {key}")
    if isinstance(getattr(cfg, key), bool):
        if value.lower() not in ("true", "false", "1", "0", "yes", "no"):
            raise click.ClickException("Expected true or false")
        value = value.lower() in ("true", "1", "yes")
    if key == "api_key":
        click.echo("Warning: API key may be saved in shell history. Prefer config init.", err=True)
    setattr(cfg, key, value)
    try:
        if key in (*FOLDER_FIELDS, "vault_path"):
            cfg.initialize_workspace()
        save_config(cfg)
    except (ValueError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps({"ok": True, "key": key}))


@config_cmd.command()
def init():
    """Configure a vault and provision a neutral workspace."""
    click.echo("Obsidian Agent CLI Setup")
    vault = click.prompt("Vault path (existing Obsidian vault directory)").strip().lstrip("\ufeff")
    defaults = Config()
    layout = {key: click.prompt(key.replace("_", " ").capitalize(), default=getattr(defaults, key))
              for key in FOLDER_FIELDS}
    api_key = click.prompt("Local REST API key (optional for offline commands)", default="", hide_input=True)
    api_url = click.prompt("API URL", default=defaults.api_url)
    verify_ssl = click.confirm("Verify TLS certificates for HTTPS API connections", default=True)
    try:
        cfg = Config(vault_path=vault, api_url=api_url, api_key=api_key,
                     api_verify_ssl=verify_ssl, **layout)
        created = cfg.initialize_workspace()
        save_config(cfg)
    except (ValueError, OSError) as exc:
        raise click.ClickException(str(exc)) from exc
    click.echo(json.dumps({"ok": True, "folders": created, "message": "Config saved. Run: obsidian-agent config show"}))
