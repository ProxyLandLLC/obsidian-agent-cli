import json
from unittest.mock import patch
import pytest
from click.testing import CliRunner
from obsidian_cli.config import Config
from obsidian_cli.registry import Registry
from obsidian_cli.commands.config_cmd import config_cmd


def test_initialize_neutral_layout(tmp_path):
    cfg = Config(vault_path=str(tmp_path))
    cfg.initialize_workspace()
    root = tmp_path / "AI Workspace"
    assert {p.name for p in root.iterdir()} == {"Raw", "Inbox", "Projects", "Reference", "registry.json"}
    assert json.loads((root / "registry.json").read_text()) == {"schema_version": 2, "projects": {}}
    (root / "Inbox" / "note.md").write_text("keep", encoding="utf-8")
    cfg.initialize_workspace()
    assert (root / "Inbox" / "note.md").read_text() == "keep"


def test_custom_layout(tmp_path):
    cfg = Config(vault_path=str(tmp_path), workspace_path="Research",
                 raw_folder="Sources", inbox_folder="Capture",
                 projects_folder="Work", reference_folder="Library")
    cfg.initialize_workspace()
    assert cfg.reference_path == "Research/Library"
    assert cfg.inbox_path == "Research/Capture"
    Registry(cfg).register_project("example")
    assert (tmp_path / "Research" / "Work" / "example" / "knowledge-log.md").is_file()


@pytest.mark.parametrize("name", ["..", "../outside", "/absolute", "a/b", "a\\b", "CON", ".obsidian"])
def test_invalid_workspace_folder(name):
    with pytest.raises(ValueError):
        Config(workspace_path=name)


def test_duplicate_subfolders_rejected():
    with pytest.raises(ValueError):
        Config(raw_folder="inbox")


def test_legacy_registry_rejected_without_mutation(tmp_path):
    root = tmp_path / "AI Workspace"
    root.mkdir()
    registry = root / "registry.json"
    registry.write_text('{"projects": {}}', encoding="utf-8")
    with pytest.raises(ValueError, match="Unsupported registry"):
        Config(vault_path=str(tmp_path)).initialize_workspace()
    assert registry.read_text() == '{"projects": {}}'
    assert not (root / "Raw").exists()


def test_config_init_creates_folders(tmp_path):
    config_dir = tmp_path / "config"
    vault = tmp_path / "vault"
    vault.mkdir()
    with patch("obsidian_cli.config.CONFIG_DIR", config_dir), \
         patch("obsidian_cli.config.CONFIG_FILE", config_dir / "config.json"), \
         patch("obsidian_cli.config.ENV_FILE", config_dir / ".env"):
        result = CliRunner().invoke(config_cmd, ["init"], input=str(vault) + "\n" * 9)
    assert result.exit_code == 0, result.output
    assert (vault / "AI Workspace" / "Reference").is_dir()
    assert json.loads((config_dir / "config.json").read_text())["projects_folder"] == "Projects"
