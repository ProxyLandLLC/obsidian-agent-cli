import json
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from obsidian_cli.commands.active import active
from obsidian_cli.config import Config


@pytest.fixture
def cfg():
    return Config(vault_path="/tmp/vault", workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


def run_active(cfg, mock_t, *args):
    runner = CliRunner()
    with patch("obsidian_cli.commands.active.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.active.Transport", return_value=mock_t):
        return runner.invoke(active, list(args))


def test_active_read(cfg):
    mock_t = MagicMock()
    mock_t.get_active.return_value = {"content": "# Open Note", "transport": "api"}
    result = run_active(cfg, mock_t, "read")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["content"] == "# Open Note"


def test_active_meta(cfg):
    mock_t = MagicMock()
    mock_t.get_active_meta.return_value = {"frontmatter": {"status": "wip"}, "transport": "api"}
    result = run_active(cfg, mock_t, "meta")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["frontmatter"]["status"] == "wip"


def test_active_write(cfg):
    mock_t = MagicMock()
    mock_t.write_active.return_value = {"ok": True, "transport": "api"}
    result = run_active(cfg, mock_t, "write", "# New content")
    assert result.exit_code == 0
    mock_t.write_active.assert_called_once_with("# New content")


def test_active_append(cfg):
    mock_t = MagicMock()
    mock_t.append_active.return_value = {"ok": True, "transport": "api"}
    result = run_active(cfg, mock_t, "append", "extra line")
    assert result.exit_code == 0
    mock_t.append_active.assert_called_once_with("extra line")


def test_active_patch(cfg):
    mock_t = MagicMock()
    mock_t.patch_active.return_value = {"ok": True, "transport": "api"}
    result = run_active(cfg, mock_t, "patch", "value", "--target", "status",
                        "--target-type", "frontmatter", "--operation", "replace")
    assert result.exit_code == 0
    mock_t.patch_active.assert_called_once_with(
        "value", "replace", "frontmatter", "status", False, False, False
    )


def test_active_delete(cfg):
    mock_t = MagicMock()
    mock_t.delete_active.return_value = {"ok": True, "transport": "api"}
    result = run_active(cfg, mock_t, "delete")
    assert result.exit_code == 0
    mock_t.delete_active.assert_called_once()
