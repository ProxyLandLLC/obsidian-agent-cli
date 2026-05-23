import json
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from obsidian_cli.commands.vault_cmd import vault_cmd
from obsidian_cli.config import Config


@pytest.fixture
def cfg():
    return Config(vault_path="/tmp/vault", workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


def run_vault(cfg, mock_t, *args):
    runner = CliRunner()
    with patch("obsidian_cli.commands.vault_cmd.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.vault_cmd.Transport", return_value=mock_t):
        return runner.invoke(vault_cmd, list(args))


def test_vault_find(cfg, tmp_path):
    mock_t = MagicMock()
    (tmp_path / "meeting-2026.md").touch()
    (tmp_path / "notes.md").touch()
    real_cfg = Config(vault_path=str(tmp_path), workspace_path="AI Workspace",
                      api_url="http://127.0.0.1:27123", api_key="test")
    runner = CliRunner()
    with patch("obsidian_cli.commands.vault_cmd.load_config", return_value=real_cfg), \
         patch("obsidian_cli.commands.vault_cmd.Transport", return_value=mock_t):
        result = runner.invoke(vault_cmd, ["find", "meeting-*.md"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["count"] == 1
    assert "meeting-2026.md" in data["matches"][0]


def test_vault_find_folder_not_found(cfg):
    mock_t = MagicMock()
    result = run_vault(cfg, mock_t, "find", "*.md", "--folder", "nonexistent")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["error"] is True


def test_vault_move(cfg):
    mock_t = MagicMock()
    mock_t.move_file.return_value = {"ok": True, "src": "old.md", "dest": "new.md", "transport": "api"}
    result = run_vault(cfg, mock_t, "move", "old.md", "new.md")
    assert result.exit_code == 0
    mock_t.move_file.assert_called_once_with("old.md", "new.md")
    data = json.loads(result.output)
    assert data["ok"] is True
