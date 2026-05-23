import json
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from obsidian_cli.commands.quickadd_cmd import quickadd_cmd
from obsidian_cli.config import Config


@pytest.fixture
def cfg():
    return Config(vault_path="/tmp/vault", workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


QA_DATA = {
    "choices": [
        {"id": "abc-123", "name": "Daily Note", "type": "Macro"},
        {"id": "def-456", "name": "New Task", "type": "Template"},
    ]
}


def run_qa(cfg, mock_t, *args, qa_data=QA_DATA):
    runner = CliRunner()
    with patch("obsidian_cli.commands.quickadd_cmd.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.quickadd_cmd.Transport", return_value=mock_t), \
         patch("obsidian_cli.commands.quickadd_cmd._load_quickadd_config", return_value=qa_data):
        return runner.invoke(quickadd_cmd, list(args))


def test_bare_quickadd_opens_modal(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    runner = CliRunner()
    with patch("obsidian_cli.commands.quickadd_cmd.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.quickadd_cmd.Transport", return_value=mock_t):
        result = runner.invoke(quickadd_cmd, [])
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("quickadd:runQuickAdd")


def test_list_choices(cfg):
    mock_t = MagicMock()
    result = run_qa(cfg, mock_t, "list")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["count"] == 2
    names = [c["name"] for c in data["choices"]]
    assert "Daily Note" in names
    assert "New Task" in names


def test_list_choices_plugin_not_found(cfg):
    mock_t = MagicMock()
    runner = CliRunner()
    with patch("obsidian_cli.commands.quickadd_cmd.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.quickadd_cmd.Transport", return_value=mock_t), \
         patch("obsidian_cli.commands.quickadd_cmd._load_quickadd_config", return_value=None):
        result = runner.invoke(quickadd_cmd, ["list"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["error"] is True


def test_run_choice_by_name(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_qa(cfg, mock_t, "run", "Daily Note")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("quickadd:choice:abc-123")
    data = json.loads(result.output)
    assert data["choice"] == "Daily Note"


def test_run_choice_case_insensitive(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_qa(cfg, mock_t, "run", "daily note")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("quickadd:choice:abc-123")


def test_run_choice_not_found(cfg):
    mock_t = MagicMock()
    result = run_qa(cfg, mock_t, "run", "Nonexistent")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["error"] is True
    assert "Nonexistent" in data["message"]
    assert "available" in data
