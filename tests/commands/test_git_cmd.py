import json
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from obsidian_cli.commands.git_cmd import git_cmd
from obsidian_cli.config import Config


@pytest.fixture
def cfg():
    return Config(vault_path="/tmp/vault", workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


def run_git(cfg, mock_t, *args):
    runner = CliRunner()
    with patch("obsidian_cli.commands.git_cmd.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.git_cmd.Transport", return_value=mock_t):
        return runner.invoke(git_cmd, list(args))


def test_git_sync_no_message(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_git(cfg, mock_t, "sync")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("obsidian-git:push")


def test_git_sync_with_message(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_git(cfg, mock_t, "sync", "-m", "feat: update notes")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("obsidian-git:commit-push-specified-message")


def test_git_commit(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_git(cfg, mock_t, "commit")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("obsidian-git:commit")


def test_git_commit_with_message(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_git(cfg, mock_t, "commit", "-m", "my message")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("obsidian-git:commit-specified-message")


def test_git_pull(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_git(cfg, mock_t, "pull")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("obsidian-git:pull")


def test_git_push(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_git(cfg, mock_t, "push")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("obsidian-git:push2")


def test_git_status(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_git(cfg, mock_t, "status")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("obsidian-git:list-changed-files")


def test_git_pause(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_git(cfg, mock_t, "pause")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("obsidian-git:pause-automatic-routines")


def test_git_branch_create(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_git(cfg, mock_t, "branch", "create")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("obsidian-git:create-branch")


def test_git_branch_switch(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_git(cfg, mock_t, "branch", "switch")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("obsidian-git:switch-branch")
