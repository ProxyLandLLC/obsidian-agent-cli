import json
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from obsidian_cli.commands.core_cmd import core_cmd
from obsidian_cli.config import Config


@pytest.fixture
def cfg():
    return Config(vault_path="/tmp/vault", workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


def run_core(cfg, mock_t, *args):
    runner = CliRunner()
    with patch("obsidian_cli.commands.core_cmd.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.core_cmd.Transport", return_value=mock_t):
        return runner.invoke(core_cmd, list(args))


def test_command_palette(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_core(cfg, mock_t, "palette")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("command-palette:open")


def test_open_search(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_core(cfg, mock_t, "search")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("global-search:open")


def test_open_settings(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_core(cfg, mock_t, "settings")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("app:open-settings")


def test_open_graph(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_core(cfg, mock_t, "graph")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("graph:open")


def test_new_tab(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_core(cfg, mock_t, "new-tab")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("workspace:new-tab")


def test_split_horizontal(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_core(cfg, mock_t, "split", "horizontal")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("workspace:split-horizontal")


def test_split_vertical(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_core(cfg, mock_t, "split", "vertical")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("workspace:split-vertical")
