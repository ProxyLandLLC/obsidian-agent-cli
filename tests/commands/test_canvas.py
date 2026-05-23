import json
import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch
from obsidian_cli.commands.canvas import canvas
from obsidian_cli.config import Config


@pytest.fixture
def vault(tmp_path):
    (tmp_path / "AI Workspace").mkdir()
    return tmp_path


@pytest.fixture
def cfg(vault):
    return Config(vault_path=str(vault), workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


def run_canvas(cfg, *args):
    runner = CliRunner()
    with patch("obsidian_cli.commands.canvas.load_config", return_value=cfg):
        result = runner.invoke(canvas, list(args))
    return result


def test_canvas_create(vault, cfg):
    result = run_canvas(cfg, "create", "overview")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["ok"] is True
    canvas_file = vault / "AI Workspace" / "overview.canvas"
    assert canvas_file.exists()
    data = json.loads(canvas_file.read_text())
    assert data["nodes"] == []
    assert data["edges"] == []


def test_canvas_read(vault, cfg):
    canvas_data = {"nodes": [{"id": "abc", "type": "text", "text": "Hi",
                               "x": 0, "y": 0, "width": 250, "height": 100}], "edges": []}
    (vault / "AI Workspace" / "test.canvas").write_text(json.dumps(canvas_data), encoding="utf-8")
    result = run_canvas(cfg, "read", "AI Workspace/test.canvas")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["nodes"][0]["text"] == "Hi"


def test_canvas_build_from_spec(vault, cfg):
    spec = json.dumps({
        "nodes": [{"type": "text", "text": "Hello"}, {"type": "text", "text": "World"}],
        "edges": [{"from": 0, "to": 1, "label": "connects"}]
    })
    result = run_canvas(cfg, "build", "diagram", "--spec", spec)
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["ok"] is True
    canvas_file = vault / "AI Workspace" / "diagram.canvas"
    data = json.loads(canvas_file.read_text())
    assert len(data["nodes"]) == 2
    assert len(data["edges"]) == 1


def test_canvas_add_text_node(vault, cfg):
    run_canvas(cfg, "create", "mycanvas")
    result = run_canvas(cfg, "add-node", "AI Workspace/mycanvas.canvas", "--type", "text", "--text", "Hello")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["ok"] is True
    data = json.loads((vault / "AI Workspace" / "mycanvas.canvas").read_text())
    assert len(data["nodes"]) == 1
    assert data["nodes"][0]["text"] == "Hello"
