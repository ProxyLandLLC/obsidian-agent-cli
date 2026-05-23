import click
from .commands.note import note
from .commands.search import search
from .commands.canvas import canvas
from .commands.teach import teach
from .commands.workspace_cmd import workspace
from .commands.periodic import periodic
from .commands.run import commands
from .commands.config_cmd import config_cmd
from .commands.active import active
from .commands.status_cmd import status_cmd
from .commands.uri import uri
from .commands.excalidraw import excalidraw
from .commands.kanban import kanban
from .commands.git_cmd import git_cmd
from .commands.tasks_cmd import tasks_cmd
from .commands.template_cmd import template_cmd
from .commands.lint_cmd import lint_cmd
from .commands.quickadd_cmd import quickadd_cmd
from .commands.refactor_cmd import refactor_cmd
from .commands.mover_cmd import mover_cmd
from .commands.meta_cmd import meta_cmd
from .commands.core_cmd import core_cmd
from .commands.vault_cmd import vault_cmd
from .commands.tags_cmd import tags_cmd
from .commands.batch_cmd import batch_cmd
from .commands.export_cmd import export_cmd


@click.group()
def cli():
    """Obsidian CLI — manage your Obsidian vault from the command line."""


cli.add_command(note)
cli.add_command(search)
cli.add_command(canvas)
cli.add_command(teach)
cli.add_command(workspace)
cli.add_command(periodic)
cli.add_command(commands)
cli.add_command(config_cmd)
cli.add_command(active)
cli.add_command(status_cmd)
cli.add_command(uri)
cli.add_command(excalidraw)
cli.add_command(kanban)
cli.add_command(git_cmd)
cli.add_command(tasks_cmd)
cli.add_command(template_cmd)
cli.add_command(lint_cmd)
cli.add_command(quickadd_cmd)
cli.add_command(refactor_cmd)
cli.add_command(mover_cmd)
cli.add_command(meta_cmd)
cli.add_command(core_cmd)
cli.add_command(vault_cmd)
cli.add_command(tags_cmd)
cli.add_command(batch_cmd)
cli.add_command(export_cmd)
