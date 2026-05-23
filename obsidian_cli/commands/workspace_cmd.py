import json
import click
from ..config import load_config
from ..registry import Registry


@click.group()
def workspace():
    """AI workspace project registry and knowledge log."""


@workspace.command()
def status():
    cfg = load_config()
    reg = Registry(cfg)
    click.echo(json.dumps(reg.status()))


@workspace.group()
def project():
    """Project subcommands."""


@project.command()
@click.argument("name")
def register(name):
    cfg = load_config()
    reg = Registry(cfg)
    result = reg.register_project(name)
    click.echo(json.dumps(result))


@project.command()
@click.argument("name")
def notes(name):
    cfg = load_config()
    reg = Registry(cfg)
    result = reg.recall(name)
    click.echo(json.dumps({"notes": result.get("notes", [])}))


@project.command()
@click.argument("name")
def canvases(name):
    cfg = load_config()
    reg = Registry(cfg)
    result = reg.recall(name)
    click.echo(json.dumps({"canvases": result.get("canvases", [])}))


@workspace.command()
@click.argument("project")
@click.argument("text")
def log(project, text):
    cfg = load_config()
    reg = Registry(cfg)
    result = reg.log(project, text)
    click.echo(json.dumps(result))


@workspace.command()
@click.argument("project")
def recall(project):
    cfg = load_config()
    reg = Registry(cfg)
    result = reg.recall(project)
    click.echo(json.dumps(result))
