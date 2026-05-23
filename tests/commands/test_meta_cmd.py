import json
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from obsidian_cli.commands.meta_cmd import meta_cmd, _parse_fields_from_fileclass
from obsidian_cli.config import Config


@pytest.fixture
def cfg():
    return Config(vault_path="/tmp/vault", workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


FILECLASS_CONTENT = """\
## Fields
- name: status
  type: Select
  options: ['active', 'archived', 'draft']
- name: priority
  type: Number
  required: true
"""


def run_meta(cfg, mock_t, *args, fields=None):
    runner = CliRunner()
    with patch("obsidian_cli.commands.meta_cmd.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.meta_cmd.Transport", return_value=mock_t), \
         patch("obsidian_cli.commands.meta_cmd._load_fileclass_fields", return_value=fields):
        return runner.invoke(meta_cmd, list(args))


def test_parse_fields_from_fileclass():
    fields = _parse_fields_from_fileclass(FILECLASS_CONTENT)
    assert len(fields) == 2
    assert fields[0]["name"] == "status"
    assert fields[0]["type"] == "Select"
    assert "active" in fields[0]["options"]
    assert fields[1]["name"] == "priority"
    assert fields[1]["required"] is True


def test_schema_found(cfg):
    mock_t = MagicMock()
    parsed = _parse_fields_from_fileclass(FILECLASS_CONTENT)
    result = run_meta(cfg, mock_t, "schema", "Book", fields=parsed)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["fileclass"] == "Book"
    assert data["count"] == 2


def test_schema_not_found(cfg):
    mock_t = MagicMock()
    result = run_meta(cfg, mock_t, "schema", "Missing", fields=None)
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["error"] is True


def test_get_field_success(cfg):
    mock_t = MagicMock()
    mock_t.get_note_meta.return_value = {
        "frontmatter": {"status": "active", "title": "My Note"},
        "transport": "api"
    }
    result = run_meta(cfg, mock_t, "get", "AI Workspace/note.md", "status")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["value"] == "active"
    assert data["field"] == "status"


def test_get_field_missing(cfg):
    mock_t = MagicMock()
    mock_t.get_note_meta.return_value = {"frontmatter": {}, "transport": "api"}
    result = run_meta(cfg, mock_t, "get", "AI Workspace/note.md", "missing_field")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["error"] is True


def test_set_field(cfg):
    mock_t = MagicMock()
    mock_t.patch_file.return_value = {"ok": True, "transport": "api"}
    result = run_meta(cfg, mock_t, "set", "AI Workspace/note.md", "status", "active")
    assert result.exit_code == 0
    mock_t.patch_file.assert_called_once_with(
        "AI Workspace/note.md", "active", "replace", "frontmatter", "status",
        True, False, False
    )
    data = json.loads(result.output)
    assert data["value"] == "active"


def test_open_ui(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_meta(cfg, mock_t, "ui")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("metadata-menu:open-field-manager")
