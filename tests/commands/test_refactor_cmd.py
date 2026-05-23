import json
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from obsidian_cli.commands.refactor_cmd import refactor_cmd
from obsidian_cli.config import Config


@pytest.fixture
def cfg():
    return Config(vault_path="/tmp/vault", workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


def run_refactor(cfg, mock_t, *args):
    runner = CliRunner()
    with patch("obsidian_cli.commands.refactor_cmd.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.refactor_cmd.Transport", return_value=mock_t):
        return runner.invoke(refactor_cmd, list(args))


def test_rename_note(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_refactor(cfg, mock_t, "rename", "AI Workspace/old.md", "new-name")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["old_path"] == "AI Workspace/old.md"
    assert data["new_name"] == "new-name"


def test_extract_heading_success(cfg):
    mock_t = MagicMock()
    mock_t.get_note.return_value = {
        "content": "# Title\n\nIntro\n\n## Section\n\nBody text\n\n## Next\n\nOther",
        "transport": "api"
    }
    mock_t.create_note.return_value = {"ok": True, "transport": "api"}
    result = run_refactor(cfg, mock_t, "extract", "AI Workspace/note.md", "## Section", "AI Workspace/section.md")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["extracted_heading"] == "Section"
    assert data["dest"] == "AI Workspace/section.md"
    created_content = mock_t.create_note.call_args[0][1]
    assert "Body text" in created_content
    assert "Other" not in created_content


def test_extract_heading_not_found(cfg):
    mock_t = MagicMock()
    mock_t.get_note.return_value = {"content": "# Title\n\nSome content", "transport": "api"}
    result = run_refactor(cfg, mock_t, "extract", "AI Workspace/note.md", "## Missing", "AI Workspace/out.md")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["error"] is True


def test_merge_notes(cfg):
    mock_t = MagicMock()
    mock_t.get_note.side_effect = [
        {"content": "# Note 1\n\nContent 1", "transport": "api"},
        {"content": "# Note 2\n\nContent 2", "transport": "api"},
    ]
    mock_t.create_note.return_value = {"ok": True, "transport": "api"}
    result = run_refactor(cfg, mock_t, "merge", "AI Workspace/a.md", "AI Workspace/b.md", "AI Workspace/merged.md")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["merged_count"] == 2
    assert data["dest"] == "AI Workspace/merged.md"
