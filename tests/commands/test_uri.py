import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch
from obsidian_cli.commands.uri import uri
from obsidian_cli.config import Config


@pytest.fixture
def cfg():
    return Config(vault_path="/my/test/vault",
                  workspace_path="AI Workspace", api_url="http://127.0.0.1:27123", api_key="test")


def run_uri(cfg, *args):
    runner = CliRunner()
    with patch("obsidian_cli.commands.uri.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.uri.subprocess.Popen") as mock_popen:
        result = runner.invoke(uri, list(args))
        return result, mock_popen


def test_uri_new_opens_obsidian(cfg):
    result, mock_popen = run_uri(cfg, "new", "--name", "My Note")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["ok"] is True
    assert "obsidian://new" in out["uri"]
    assert "My%20Note" in out["uri"] or "My+Note" in out["uri"] or "My Note" in out["uri"]
    mock_popen.assert_called_once()


def test_uri_new_silent_flag(cfg):
    result, mock_popen = run_uri(cfg, "new", "--name", "Note", "--silent")
    out = json.loads(result.output)
    assert "silent=true" in out["uri"]


def test_uri_search(cfg):
    result, mock_popen = run_uri(cfg, "search", "#project status:active")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert "obsidian://search" in out["uri"]
    mock_popen.assert_called_once()
