import json
import click
from ..config import load_config
from ..transport import Transport


@click.group("git")
def git_cmd():
    """Obsidian Git plugin commands (requires Obsidian Git plugin)."""


@git_cmd.command()
@click.option("-m", "--message", default="", help="Commit message (enables commit-specified-message)")
def sync(message):
    """Commit all changes and push. Without -m uses auto message; with -m commits with specified message."""
    cfg = load_config()
    t = Transport(cfg)
    if message:
        result = t.run_command("obsidian-git:commit-push-specified-message")
    else:
        result = t.run_command("obsidian-git:push")
    click.echo(json.dumps(result))


@git_cmd.command()
@click.option("-m", "--message", default="", help="Commit message")
def commit(message):
    """Commit all changes."""
    cfg = load_config()
    t = Transport(cfg)
    if message:
        result = t.run_command("obsidian-git:commit-specified-message")
    else:
        result = t.run_command("obsidian-git:commit")
    click.echo(json.dumps(result))


@git_cmd.command()
def pull():
    """Pull latest changes from remote."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("obsidian-git:pull")
    click.echo(json.dumps(result))


@git_cmd.command()
def push():
    """Push committed changes to remote."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("obsidian-git:push2")
    click.echo(json.dumps(result))


@git_cmd.command()
def status():
    """List changed files in Obsidian Git source control view."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("obsidian-git:list-changed-files")
    click.echo(json.dumps(result))


@git_cmd.command()
def pause():
    """Pause or resume Obsidian Git automatic routines."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("obsidian-git:pause-automatic-routines")
    click.echo(json.dumps(result))


@git_cmd.command()
def fetch():
    """Fetch from remote without merging."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("obsidian-git:fetch")
    click.echo(json.dumps(result))


@git_cmd.group()
def branch():
    """Branch operations."""


@branch.command("create")
def branch_create():
    """Create a new branch (opens Obsidian prompt)."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("obsidian-git:create-branch")
    click.echo(json.dumps(result))


@branch.command("switch")
def branch_switch():
    """Switch to a branch (opens Obsidian branch picker)."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("obsidian-git:switch-branch")
    click.echo(json.dumps(result))


@branch.command("delete")
def branch_delete():
    """Delete a branch (opens Obsidian branch picker)."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("obsidian-git:delete-branch")
    click.echo(json.dumps(result))
