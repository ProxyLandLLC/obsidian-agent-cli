import json
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from obsidian_cli.commands.template_cmd import template_cmd
from obsidian_cli.config import Config


@pytest.fixture
def cfg():
    return Config(vault_path="/tmp/vault", workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


def run_template(cfg, mock_t, *args):
    runner = CliRunner()
    with patch("obsidian_cli.commands.template_cmd.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.template_cmd.Transport", return_value=mock_t):
        return runner.invoke(template_cmd, list(args))


def test_template_insert(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_template(cfg, mock_t, "insert")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("templater-obsidian:insert-templater")


def test_template_create_no_name(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_template(cfg, mock_t, "create")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("templater-obsidian:create-new-note-from-template")


def test_template_apply(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_template(cfg, mock_t, "apply")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("templater-obsidian:replace-in-file-templater")
