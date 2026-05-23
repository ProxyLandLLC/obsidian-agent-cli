import json
import click
from ..config import load_config
from ..transport import Transport


@click.command("lint")
@click.option("--all", "lint_all", is_flag=True, default=False, help="Lint all files in vault")
@click.option("--folder", "lint_folder", is_flag=True, default=False,
              help="Lint all files in current folder (Obsidian context)")
def lint_cmd(lint_all, lint_folder):
    """Lint notes with Obsidian Linter (requires Obsidian Linter plugin).

    Default: lints the currently active file.
    --all: lints every file in the vault.
    --folder: lints all files in the current Obsidian folder context.
    """
    cfg = load_config()
    t = Transport(cfg)
    if lint_all:
        result = t.run_command("obsidian-linter:lint-all-files")
    elif lint_folder:
        result = t.run_command("obsidian-linter:lint-all-files-in-folder")
    else:
        result = t.run_command("obsidian-linter:lint-file")
    click.echo(json.dumps(result))
