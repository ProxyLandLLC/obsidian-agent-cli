import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from obsidian_cli.commands.kanban import kanban
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
        with patch("obsidian_cli.commands.kanban.load_config", return_value=cfg), \
             patch("obsidian_cli.commands.kanban.Transport", return_value=real_transport):
            return runner.invoke(kanban, list(args))
    return run


def test_kanban_create(vault, cfg):
    run = make_runner(cfg)
    result = run("create", "AI Workspace/board.md", "--lanes", "To Do,In Progress,Done")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["ok"] is True
    content = (vault / "AI Workspace" / "board.md").read_text(encoding="utf-8")
    assert "## To Do" in content
    assert "## In Progress" in content
    assert "kanban-plugin: basic" in content


def test_kanban_card_add(vault, cfg):
    run = make_runner(cfg)
    run("create", "AI Workspace/board.md", "--lanes", "Backlog,Done")
    result = run("card", "add", "AI Workspace/board.md", "Backlog", "My first task")
    assert result.exit_code == 0
    content = (vault / "AI Workspace" / "board.md").read_text(encoding="utf-8")
    assert "- [ ] My first task" in content


def test_kanban_card_add_to_nonexistent_lane(vault, cfg):
    run = make_runner(cfg)
    run("create", "AI Workspace/board.md", "--lanes", "Backlog")
    result = run("card", "add", "AI Workspace/board.md", "Sprint", "task")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["error"] is True


def test_kanban_lane_add(vault, cfg):
    run = make_runner(cfg)
    run("create", "AI Workspace/board.md", "--lanes", "To Do")
    result = run("lane", "add", "AI Workspace/board.md", "Review")
    assert result.exit_code == 0
    content = (vault / "AI Workspace" / "board.md").read_text(encoding="utf-8")
    assert "## Review" in content


def test_kanban_read(vault, cfg):
    run = make_runner(cfg)
    run("create", "AI Workspace/board.md", "--lanes", "To Do,Done")
    run("card", "add", "AI Workspace/board.md", "To Do", "Task X")
    result = run("read", "AI Workspace/board.md")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert "To Do" in out["lanes"]
    assert any("Task X" in c["text"] for c in out["lanes"]["To Do"])
