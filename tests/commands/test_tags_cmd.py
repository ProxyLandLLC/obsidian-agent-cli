import json
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from obsidian_cli.commands.tags_cmd import tags_cmd
from obsidian_cli.config import Config


@pytest.fixture
def cfg():
    return Config(vault_path="/tmp/vault", workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


def run_tags(cfg, mock_t, *args):
    runner = CliRunner()
    with patch("obsidian_cli.commands.tags_cmd.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.tags_cmd.Transport", return_value=mock_t):
        return runner.invoke(tags_cmd, list(args))


def test_rename_tag(cfg):
    mock_t = MagicMock()
    mock_t.rename_tag_in_vault.return_value = {
        "old_tag": "#todo", "new_tag": "#task",
        "changed_count": 3, "changed": ["a.md", "b.md", "c.md"],
        "dry_run": False, "transport": "fs",
    }
    result = run_tags(cfg, mock_t, "rename", "#todo", "#task")
    assert result.exit_code == 0
    mock_t.rename_tag_in_vault.assert_called_once_with("#todo", "#task", dry_run=False)
    data = json.loads(result.output)
    assert data["changed_count"] == 3


def test_rename_tag_dry_run(cfg):
    mock_t = MagicMock()
    mock_t.rename_tag_in_vault.return_value = {
        "old_tag": "#todo", "new_tag": "#task",
        "changed_count": 2, "changed": ["a.md", "b.md"],
        "dry_run": True, "transport": "fs",
    }
    result = run_tags(cfg, mock_t, "rename", "#todo", "#task", "--dry-run")
    assert result.exit_code == 0
    mock_t.rename_tag_in_vault.assert_called_once_with("#todo", "#task", dry_run=True)
    data = json.loads(result.output)
    assert data["dry_run"] is True
