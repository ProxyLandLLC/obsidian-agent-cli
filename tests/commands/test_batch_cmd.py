import json
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from obsidian_cli.commands.batch_cmd import batch_cmd, _iter_notes
from obsidian_cli.config import Config


@pytest.fixture
def vault(tmp_path):
    (tmp_path / "AI Workspace").mkdir()
    (tmp_path / "AI Workspace" / "a.md").write_text("# Note A\n\nContent A", encoding="utf-8")
    (tmp_path / "AI Workspace" / "b.md").write_text("# Note B\n\nContent B", encoding="utf-8")
    obsidian = tmp_path / ".obsidian"
    obsidian.mkdir()
    (obsidian / "hidden.md").write_text("hidden", encoding="utf-8")
    return tmp_path


@pytest.fixture
def cfg(vault):
    return Config(vault_path=str(vault), workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


def run_batch(cfg, mock_t, *args):
    runner = CliRunner()
    with patch("obsidian_cli.commands.batch_cmd.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.batch_cmd.Transport", return_value=mock_t):
        return runner.invoke(batch_cmd, list(args))


def test_iter_notes_excludes_obsidian(vault):
    notes = _iter_notes(str(vault))
    assert all(".obsidian" not in n for n in notes)
    assert any("AI Workspace" in n for n in notes)


def test_batch_frontmatter_dry_run(cfg):
    mock_t = MagicMock()
    result = run_batch(cfg, mock_t, "frontmatter", "status", "active",
                       "--folder", "AI Workspace", "--dry-run")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["dry_run"] is True
    assert data["changed_count"] == 2
    mock_t.patch_file.assert_not_called()


def test_batch_frontmatter_applies(cfg):
    mock_t = MagicMock()
    mock_t.patch_file.return_value = {"ok": True, "transport": "api"}
    result = run_batch(cfg, mock_t, "frontmatter", "status", "active", "--folder", "AI Workspace")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["changed_count"] == 2
    assert mock_t.patch_file.call_count == 2


def test_batch_rename_literal(cfg, vault):
    (vault / "AI Workspace" / "a.md").write_text("# A\n\nOld Company Name", encoding="utf-8")
    mock_t = MagicMock()
    result = run_batch(cfg, mock_t, "rename", "Old Company Name", "New Company Name",
                       "--folder", "AI Workspace")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["changed_count"] == 1
    assert "New Company Name" in (vault / "AI Workspace" / "a.md").read_text(encoding="utf-8")


def test_batch_rename_regex(cfg, vault):
    (vault / "AI Workspace" / "a.md").write_text("# A\n\nDate: 2025-01-15", encoding="utf-8")
    mock_t = MagicMock()
    result = run_batch(cfg, mock_t, "rename", r"\d{4}-\d{2}-\d{2}", "REDACTED",
                       "--folder", "AI Workspace", "--regex")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["changed_count"] == 1


def test_batch_rename_dry_run(cfg, vault):
    (vault / "AI Workspace" / "a.md").write_text("# A\n\nfoo bar", encoding="utf-8")
    original = (vault / "AI Workspace" / "a.md").read_text(encoding="utf-8")
    mock_t = MagicMock()
    result = run_batch(cfg, mock_t, "rename", "foo", "baz", "--folder", "AI Workspace", "--dry-run")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["dry_run"] is True
    assert (vault / "AI Workspace" / "a.md").read_text(encoding="utf-8") == original
