import json
import click
from pathlib import Path
from ..config import load_config
from ..transport import Transport
from ..canvas_builder import CanvasBuilder


@click.group()
def canvas():
    """Canvas creation and management."""


@canvas.command()
@click.argument("name")
@click.option("--folder", default=None, help="Vault path for canvas (default: AI Workspace/)")
def create(name, folder):
    cfg = load_config()
    if folder is None:
        folder = cfg.workspace_path
    vault_path = f"{folder}/{name}.canvas"
    abs_path = Path(cfg.vault_path) / vault_path
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_text(json.dumps({"nodes": [], "edges": []}, indent=2), encoding="utf-8")
    click.echo(json.dumps({"ok": True, "path": vault_path}))


@canvas.command()
@click.argument("canvas_path")
def read(canvas_path):
    cfg = load_config()
    abs_path = Path(cfg.vault_path) / canvas_path
    if not abs_path.exists():
        click.echo(json.dumps({"error": True, "message": f"Not found: {canvas_path}"}))
        return
    data = json.loads(abs_path.read_text(encoding="utf-8"))
    click.echo(json.dumps(data))


@canvas.command("add-node")
@click.argument("canvas_path")
@click.option("--type", "node_type", required=True,
              type=click.Choice(["text", "file", "link", "group"]))
@click.option("--text", default="")
@click.option("--file", "file_path", default="")
@click.option("--url", default="")
@click.option("--label", default="")
@click.option("--color", default="")
def add_node(canvas_path, node_type, text, file_path, url, label, color):
    cfg = load_config()
    abs_path = Path(cfg.vault_path) / canvas_path
    if not abs_path.exists():
        click.echo(json.dumps({"error": True, "message": f"Canvas not found: {canvas_path}"}))
        return
    data = json.loads(abs_path.read_text(encoding="utf-8"))
    cb = CanvasBuilder()
    cb._nodes = data["nodes"]
    cb._edges = data["edges"]
    if node_type == "text":
        nid = cb.add_text_node(text, color=color)
    elif node_type == "file":
        nid = cb.add_file_node(file_path, color=color)
    elif node_type == "link":
        nid = cb.add_link_node(url, color=color)
    elif node_type == "group":
        nid = cb.add_group_node(label=label, color=color)
    else:
        click.echo(json.dumps({"error": True, "message": f"Unknown node type: {node_type}"}))
        return
    abs_path.write_text(cb.to_json(), encoding="utf-8")
    click.echo(json.dumps({"ok": True, "node_id": nid}))


@canvas.command("add-edge")
@click.argument("canvas_path")
@click.argument("from_id")
@click.argument("to_id")
@click.option("--label", default="")
@click.option("--color", default="")
def add_edge(canvas_path, from_id, to_id, label, color):
    cfg = load_config()
    abs_path = Path(cfg.vault_path) / canvas_path
    if not abs_path.exists():
        click.echo(json.dumps({"error": True, "message": f"Canvas not found: {canvas_path}"}))
        return
    data = json.loads(abs_path.read_text(encoding="utf-8"))
    cb = CanvasBuilder()
    cb._nodes = data["nodes"]
    cb._edges = data["edges"]
    eid = cb.add_edge(from_id, to_id, label=label, color=color)
    abs_path.write_text(cb.to_json(), encoding="utf-8")
    click.echo(json.dumps({"ok": True, "edge_id": eid}))


@canvas.command()
@click.argument("name")
@click.option("--spec", required=True, help="JSON spec string")
@click.option("--folder", default=None)
def build(name, spec, folder):
    cfg = load_config()
    if folder is None:
        folder = cfg.workspace_path
    try:
        spec_data = json.loads(spec)
    except json.JSONDecodeError as e:
        click.echo(json.dumps({"error": True, "message": f"Invalid JSON spec: {e}"}))
        return
    cb = CanvasBuilder.from_spec(spec_data)
    vault_path = f"{folder}/{name}.canvas"
    abs_path = Path(cfg.vault_path) / vault_path
    abs_path.parent.mkdir(parents=True, exist_ok=True)
    abs_path.write_text(cb.to_json(), encoding="utf-8")
    click.echo(json.dumps({"ok": True, "path": vault_path,
                            "nodes": len(cb._nodes), "edges": len(cb._edges)}))


@canvas.command("open")
@click.argument("canvas_path")
def open_canvas(canvas_path):
    cfg = load_config()
    t = Transport(cfg)
    result = t.open_in_obsidian(canvas_path)
    click.echo(json.dumps(result))
