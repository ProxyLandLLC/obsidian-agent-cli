import json
import pytest
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch
from obsidian_cli.commands.excalidraw import excalidraw
from obsidian_cli.config import Config
from obsidian_cli.transport import Transport


@pytest.fixture
def vault(tmp_path):
    (tmp_path / "AI Workspace").mkdir()
    return tmp_path


@pytest.fixture
def cfg(vault):
    return Config(vault_path=str(vault), workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


def make_runner(cfg):
    def run(*args):
        runner = CliRunner()
        real_transport = Transport(cfg)
        real_transport._api_available = False
        with patch("obsidian_cli.commands.excalidraw.load_config", return_value=cfg), \
             patch("obsidian_cli.commands.excalidraw.Transport", return_value=real_transport):
            return runner.invoke(excalidraw, list(args))
    return run


def test_excalidraw_create(vault, cfg):
    run = make_runner(cfg)
    result = run("create", "AI Workspace/diagram.excalidraw")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["ok"] is True
    file_path = vault / "AI Workspace" / "diagram.excalidraw"
    assert file_path.exists()
    data = json.loads(file_path.read_text(encoding="utf-8"))
    assert data["type"] == "excalidraw"
    assert data["version"] == 2


def test_excalidraw_add_shape(vault, cfg):
    run = make_runner(cfg)
    run("create", "AI Workspace/diagram.excalidraw")
    result = run("add-shape", "AI Workspace/diagram.excalidraw",
                 "--type", "rectangle", "--label", "My Box")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["ok"] is True
    data = json.loads((vault / "AI Workspace" / "diagram.excalidraw").read_text(encoding="utf-8"))
    rects = [e for e in data["elements"] if e["type"] == "rectangle"]
    assert len(rects) == 1


def test_excalidraw_read(vault, cfg):
    run = make_runner(cfg)
    run("create", "AI Workspace/diagram.excalidraw")
    result = run("read", "AI Workspace/diagram.excalidraw")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert "elements" in out


def test_excalidraw_build_from_spec(vault, cfg):
    run = make_runner(cfg)
    spec = json.dumps({
        "elements": [
            {"type": "rectangle", "label": "Start"},
            {"type": "ellipse", "label": "Process"},
        ],
        "arrows": [{"from": 0, "to": 1, "label": "goes to"}],
    })
    result = run("build", "AI Workspace/flow.excalidraw", "--spec", spec)
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["ok"] is True
    assert out["elements"] == 2
    assert out["arrows"] == 1
    file_path = vault / "AI Workspace" / "flow.excalidraw"
    assert file_path.exists()


def test_excalidraw_open(vault, cfg):
    run = make_runner(cfg)
    run("create", "AI Workspace/diagram.excalidraw")
    with patch("obsidian_cli.commands.excalidraw.subprocess.Popen") as mock_popen:
        result = run("open", "AI Workspace/diagram.excalidraw")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["ok"] is True
