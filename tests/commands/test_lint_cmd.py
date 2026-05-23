import json
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from obsidian_cli.commands.lint_cmd import lint_cmd
from obsidian_cli.config import Config


@pytest.fixture
def cfg():
    return Config(vault_path="/tmp/vault", workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


def run_lint(cfg, mock_t, *args):
    runner = CliRunner()
    with patch("obsidian_cli.commands.lint_cmd.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.lint_cmd.Transport", return_value=mock_t):
        return runner.invoke(lint_cmd, list(args))


def test_lint_active_file(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_lint(cfg, mock_t)
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("obsidian-linter:lint-file")


def test_lint_all(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_lint(cfg, mock_t, "--all")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("obsidian-linter:lint-all-files")


def test_lint_folder(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_lint(cfg, mock_t, "--folder")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("obsidian-linter:lint-all-files-in-folder")
