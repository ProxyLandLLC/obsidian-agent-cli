import json
import click
from ..config import load_config
from ..transport import Transport
from ..kanban_builder import KanbanBuilder


@click.group()
def kanban():
    """Obsidian Kanban board management (requires Kanban plugin)."""


@kanban.command()
@click.argument("path")
@click.option("--lanes", default="To Do,In Progress,Done",
              help="Comma-separated lane names")
def create(path, lanes):
    """Create a new Kanban board with the given lanes."""
    cfg = load_config()
    t = Transport(cfg)
    kb = KanbanBuilder()
    for lane in lanes.split(","):
        kb.add_lane(lane.strip())
    result = t.write_file(path, kb.to_markdown())
    if "ok" in result:
        result["path"] = path
        result["lanes"] = [l.strip() for l in lanes.split(",")]
    click.echo(json.dumps(result))


@kanban.command()
@click.argument("path")
def read(path):
    """Read a Kanban board and return its lanes and cards."""
    cfg = load_config()
    t = Transport(cfg)
    raw = t.read_file(path)
    if "error" in raw:
        click.echo(json.dumps(raw))
        return
    kb = KanbanBuilder.from_markdown(raw["content"])
    click.echo(json.dumps({
        "lanes": {
            lane: kb._lanes[lane]
            for lane in kb._lane_order
        },
        "transport": raw["transport"],
    }))


@kanban.group()
def card():
    """Card operations within a Kanban board."""


@card.command("add")
@click.argument("path")
@click.argument("lane")
@click.argument("text")
@click.option("--done", is_flag=True, default=False, help="Mark card as done")
def card_add(path, lane, text, done):
    """Add a card to a lane in a Kanban board."""
    cfg = load_config()
    t = Transport(cfg)
    raw = t.read_file(path)
    if "error" in raw:
        click.echo(json.dumps(raw))
        return
    kb = KanbanBuilder.from_markdown(raw["content"])
    try:
        kb.add_card(lane, text, done=done)
    except ValueError as e:
        click.echo(json.dumps({"error": True, "message": str(e)}))
        return
    result = t.write_file(path, kb.to_markdown())
    if "ok" in result:
        result["card"] = text
        result["lane"] = lane
    click.echo(json.dumps(result))


@kanban.group()
def lane():
    """Lane operations within a Kanban board."""


@lane.command("add")
@click.argument("path")
@click.argument("name")
def lane_add(path, name):
    """Add a new lane to an existing Kanban board."""
    cfg = load_config()
    t = Transport(cfg)
    raw = t.read_file(path)
    if "error" in raw:
        click.echo(json.dumps(raw))
        return
    kb = KanbanBuilder.from_markdown(raw["content"])
    kb.add_lane(name)
    result = t.write_file(path, kb.to_markdown())
    if "ok" in result:
        result["lane"] = name
    click.echo(json.dumps(result))


@kanban.command()
@click.argument("path")
def archive(path):
    """Archive completed cards (trigger Kanban plugin command)."""
    cfg = load_config()
    t = Transport(cfg)
    result = t.run_command("obsidian-kanban:archive-completed-cards")
    click.echo(json.dumps(result))
