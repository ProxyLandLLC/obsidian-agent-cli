import json
import pytest
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from obsidian_cli.commands.tasks_cmd import tasks_cmd
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
        with patch("obsidian_cli.commands.tasks_cmd.load_config", return_value=cfg), \
             patch("obsidian_cli.commands.tasks_cmd.Transport", return_value=real_transport):
            return runner.invoke(tasks_cmd, list(args))
    return run


def test_tasks_add_basic(vault, cfg):
    run = make_runner(cfg)
    result = run("add", "Fix the bug", "--file", "AI Workspace/tasks.md")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["ok"] is True
    content = (vault / "AI Workspace" / "tasks.md").read_text(encoding="utf-8")
    assert "- [ ] Fix the bug" in content


def test_tasks_add_with_due(vault, cfg):
    run = make_runner(cfg)
    run("add", "Review PR", "--file", "AI Workspace/tasks.md", "--due", "2026-05-20")
    content = (vault / "AI Workspace" / "tasks.md").read_text(encoding="utf-8")
    assert "📅 2026-05-20" in content


def test_tasks_add_with_priority_high(vault, cfg):
    run = make_runner(cfg)
    run("add", "Urgent task", "--file", "AI Workspace/tasks.md", "--priority", "high")
    content = (vault / "AI Workspace" / "tasks.md").read_text(encoding="utf-8")
    assert "🔼" in content


def test_tasks_add_with_priority_highest(vault, cfg):
    run = make_runner(cfg)
    run("add", "Critical", "--file", "AI Workspace/tasks.md", "--priority", "highest")
    content = (vault / "AI Workspace" / "tasks.md").read_text(encoding="utf-8")
    assert "⏫" in content


def test_tasks_add_with_recur(vault, cfg):
    run = make_runner(cfg)
    run("add", "Weekly review", "--file", "AI Workspace/tasks.md", "--recur", "every week")
    content = (vault / "AI Workspace" / "tasks.md").read_text(encoding="utf-8")
    assert "🔁 every week" in content


def test_tasks_add_appends_to_existing(vault, cfg):
    (vault / "AI Workspace" / "tasks.md").write_text("# Tasks\n\n- [ ] Existing task\n", encoding="utf-8")
    run = make_runner(cfg)
    run("add", "New task", "--file", "AI Workspace/tasks.md")
    content = (vault / "AI Workspace" / "tasks.md").read_text(encoding="utf-8")
    assert "Existing task" in content
    assert "New task" in content


def test_tasks_list(vault, cfg):
    (vault / "AI Workspace" / "tasks.md").write_text(
        "- [ ] Open task\n- [x] Done task\n- [ ] Another open\n", encoding="utf-8"
    )
    run = make_runner(cfg)
    result = run("list", "--folder", "AI Workspace")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert "tasks" in out
    open_tasks = [t for t in out["tasks"] if not t["done"]]
    done_tasks = [t for t in out["tasks"] if t["done"]]
    assert len(open_tasks) == 2
    assert len(done_tasks) == 1


def test_tasks_list_open_only(vault, cfg):
    (vault / "AI Workspace" / "tasks.md").write_text(
        "- [ ] Open task\n- [x] Done task\n", encoding="utf-8"
    )
    run = make_runner(cfg)
    result = run("list", "--folder", "AI Workspace", "--open-only")
    out = json.loads(result.output)
    assert all(not t["done"] for t in out["tasks"])


def test_tasks_ui_calls_run_command(cfg):
    runner = CliRunner()
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    with patch("obsidian_cli.commands.tasks_cmd.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.tasks_cmd.Transport", return_value=mock_t):
        result = runner.invoke(tasks_cmd, ["ui"])
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("obsidian-tasks-plugin:create-or-edit-task")
