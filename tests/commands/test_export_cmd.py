import json
import pytest
from pathlib import Path
from click.testing import CliRunner
from unittest.mock import patch
from obsidian_cli.commands.export_cmd import export_cmd
from obsidian_cli.config import Config


@pytest.fixture
def vault(tmp_path):
    chief = tmp_path / "AI Workspace"
    chief.mkdir()
    (chief / "note1.md").write_text("# Note 1\n\nContent 1", encoding="utf-8")
    (chief / "note2.md").write_text("# Note 2\n\nContent 2", encoding="utf-8")
    (tmp_path / ".obsidian").mkdir()
    (tmp_path / ".obsidian" / "config").write_text("{}", encoding="utf-8")
    return tmp_path


@pytest.fixture
def cfg(vault):
    return Config(vault_path=str(vault), workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


def run_export(cfg, *args):
    runner = CliRunner()
    with patch("obsidian_cli.commands.export_cmd.load_config", return_value=cfg):
        return runner.invoke(export_cmd, list(args))


def test_export_bundle_creates_file(cfg, vault, tmp_path):
    out = str(tmp_path / "bundle.md")
    result = run_export(cfg, "bundle", out, "--folder", "AI Workspace")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["ok"] is True
    assert data["files"] == 2
    content = Path(out).read_text(encoding="utf-8")
    assert "Note 1" in content
    assert "Note 2" in content
    assert "<!-- source:" in content


def test_export_bundle_folder_not_found(cfg):
    result = run_export(cfg, "bundle", "--folder", "NonExistent")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["error"] is True


def test_export_bundle_excludes_obsidian(cfg, vault, tmp_path):
    out = str(tmp_path / "bundle.md")
    run_export(cfg, "bundle", out)
    content = Path(out).read_text(encoding="utf-8")
    assert ".obsidian" not in content
