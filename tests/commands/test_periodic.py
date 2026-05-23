import json
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from obsidian_cli.commands.periodic import periodic
from obsidian_cli.config import Config


@pytest.fixture
def cfg():
    return Config(vault_path="/tmp/vault", workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


def run_periodic(cfg, mock_t, *args):
    runner = CliRunner()
    with patch("obsidian_cli.commands.periodic.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.periodic.Transport", return_value=mock_t):
        return runner.invoke(periodic, list(args))


def test_periodic_write(cfg):
    mock_t = MagicMock()
    mock_t.write_periodic.return_value = {"ok": True, "transport": "api"}
    result = run_periodic(cfg, mock_t, "write", "daily", "# Today\n\nMy notes")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["ok"] is True
    mock_t.write_periodic.assert_called_once_with("daily", "# Today\n\nMy notes")


def test_periodic_append(cfg):
    mock_t = MagicMock()
    mock_t.append_periodic.return_value = {"ok": True, "transport": "api"}
    result = run_periodic(cfg, mock_t, "append", "daily", "new entry")
    assert result.exit_code == 0
    mock_t.append_periodic.assert_called_once_with("daily", "new entry")


def test_periodic_delete(cfg):
    mock_t = MagicMock()
    mock_t.delete_periodic.return_value = {"ok": True, "transport": "api"}
    result = run_periodic(cfg, mock_t, "delete", "weekly")
    assert result.exit_code == 0
    mock_t.delete_periodic.assert_called_once_with("weekly")


def test_periodic_date_read(cfg):
    mock_t = MagicMock()
    mock_t.get_periodic_date.return_value = {"content": "# Notes", "transport": "api"}
    result = run_periodic(cfg, mock_t, "date", "daily", "2026-05-11")
    assert result.exit_code == 0
    mock_t.get_periodic_date.assert_called_once_with("daily", 2026, 5, 11)


def test_periodic_date_write(cfg):
    mock_t = MagicMock()
    mock_t.write_periodic_date.return_value = {"ok": True, "transport": "api"}
    result = run_periodic(cfg, mock_t, "date", "daily", "2026-05-11", "--write", "# Content")
    assert result.exit_code == 0
    mock_t.write_periodic_date.assert_called_once_with("daily", 2026, 5, 11, "# Content")


def test_periodic_date_invalid_format(cfg):
    mock_t = MagicMock()
    result = run_periodic(cfg, mock_t, "date", "daily", "05-11-2026")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["error"] is True


def test_periodic_nav_prev(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_periodic(cfg, mock_t, "nav", "daily", "prev")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("periodic-notes:prev-daily")


def test_periodic_nav_next(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_periodic(cfg, mock_t, "nav", "weekly", "next")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("periodic-notes:next-weekly")
