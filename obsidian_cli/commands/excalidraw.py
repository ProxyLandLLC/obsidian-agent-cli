import json
import subprocess
import sys
from pathlib import Path
from urllib.parse import quote
import click
from ..config import load_config
from ..transport import Transport
from ..excalidraw_builder import ExcalidrawBuilder


@click.group()
def excalidraw():
    """Excalidraw whiteboard diagrams (.excalidraw files)."""


@excalidraw.command()
@click.argument("path")
def create(path):
    """Create a new empty Excalidraw drawing."""
    cfg = load_config()
    t = Transport(cfg)
    eb = ExcalidrawBuilder()
    result = t.write_file(path, eb.to_json())
    if "ok" in result:
        result["path"] = path
    click.echo(json.dumps(result))


@excalidraw.command("add-shape")
@click.argument("path")
@click.option("--type", "shape_type",
              type=click.Choice(["rectangle", "ellipse", "diamond", "text"]),
              default="rectangle")
@click.option("--label", default="", help="Shape label or text content")
@click.option("--stroke-color", default="#1e1e2e")
@click.option("--background-color", default="transparent")
@click.option("--width", default=200, type=int)
@click.option("--height", default=100, type=int)
def add_shape(path, shape_type, label, stroke_color, background_color, width, height):
    """Add a shape to an existing Excalidraw drawing."""
    cfg = load_config()
    t = Transport(cfg)
    raw = t.read_file(path)
    if "error" in raw:
        click.echo(json.dumps(raw))
        return
    data = json.loads(raw["content"])
    eb = ExcalidrawBuilder()
    eb._elements = data.get("elements", [])
    if shape_type == "rectangle":
        nid = eb.add_rectangle(label, stroke_color=stroke_color,
                               background_color=background_color, width=width, height=height)
    elif shape_type == "ellipse":
        nid = eb.add_ellipse(label, stroke_color=stroke_color,
                             background_color=background_color, width=width, height=height)
    elif shape_type == "diamond":
        nid = eb.add_diamond(label, stroke_color=stroke_color,
                             background_color=background_color, width=width, height=height)
    else:
        nid = eb.add_text(label)
    data["elements"] = eb._elements
    result = t.write_file(path, json.dumps(data, indent=2))
    if "ok" in result:
        result["element_id"] = nid
    click.echo(json.dumps(result))


@excalidraw.command("add-arrow")
@click.argument("path")
@click.argument("from_id")
@click.argument("to_id")
@click.option("--label", default="")
@click.option("--stroke-color", default="#1e1e2e")
def add_arrow(path, from_id, to_id, label, stroke_color):
    """Add an arrow between two elements in an Excalidraw drawing."""
    cfg = load_config()
    t = Transport(cfg)
    raw = t.read_file(path)
    if "error" in raw:
        click.echo(json.dumps(raw))
        return
    data = json.loads(raw["content"])
    eb = ExcalidrawBuilder()
    eb._elements = data.get("elements", [])
    arrow_id = eb.add_arrow(from_id, to_id, label=label, stroke_color=stroke_color)
    data["elements"] = eb._elements
    result = t.write_file(path, json.dumps(data, indent=2))
    if "ok" in result:
        result["arrow_id"] = arrow_id
    click.echo(json.dumps(result))


@excalidraw.command()
@click.argument("path")
def read(path):
    """Read an Excalidraw drawing and return its elements as JSON."""
    cfg = load_config()
    t = Transport(cfg)
    raw = t.read_file(path)
    if "error" in raw:
        click.echo(json.dumps(raw))
        return
    data = json.loads(raw["content"])
    click.echo(json.dumps({
        "elements": data.get("elements", []),
        "element_count": len(data.get("elements", [])),
        "transport": raw["transport"],
    }))


@excalidraw.command()
@click.argument("path")
@click.option("--spec", required=True, help="JSON spec: {elements: [...], arrows: [...]}")
def build(path, spec):
    """Build a complete Excalidraw drawing from a JSON spec in one shot."""
    try:
        spec_data = json.loads(spec)
    except json.JSONDecodeError as e:
        click.echo(json.dumps({"error": True, "message": f"Invalid JSON spec: {e}"}))
        return
    cfg = load_config()
    t = Transport(cfg)
    eb = ExcalidrawBuilder.from_spec(spec_data)
    shape_count = sum(1 for e in eb._elements if e["type"] not in ("arrow", "line"))
    arrow_count = sum(1 for e in eb._elements if e["type"] in ("arrow", "line"))
    result = t.write_file(path, eb.to_json())
    if "ok" in result:
        result.update({"path": path, "elements": shape_count, "arrows": arrow_count})
    click.echo(json.dumps(result))


@excalidraw.command("open")
@click.argument("path")
def open_drawing(path):
    """Open an Excalidraw drawing in Obsidian."""
    cfg = load_config()
    vault_name = Path(cfg.vault_path).name
    uri = f"obsidian://open?vault={quote(vault_name)}&file={quote(path)}"
    if sys.platform == "win32":
        subprocess.Popen(["cmd", "/c", "start", uri], shell=False)
    elif sys.platform == "darwin":
        subprocess.Popen(["open", uri])
    else:
        subprocess.Popen(["xdg-open", uri])
    click.echo(json.dumps({"ok": True, "uri": uri, "transport": "uri"}))
