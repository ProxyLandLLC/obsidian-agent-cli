import json
import pytest
from pathlib import Path
from obsidian_cli.config import Config
from obsidian_cli.registry import Registry


@pytest.fixture
def vault(tmp_path):
    chief = tmp_path / "AI Workspace"
    chief.mkdir()
    return tmp_path


@pytest.fixture
def cfg(vault):
    return Config(vault_path=str(vault), workspace_path="AI Workspace")


def test_register_creates_project(vault, cfg):
    reg = Registry(cfg)
    reg.register_project("my-project")
    data = json.loads((vault / "AI Workspace" / "registry.json").read_text())
    assert "my-project" in data["projects"]


def test_register_creates_project_folder(vault, cfg):
    reg = Registry(cfg)
    reg.register_project("my-project")
    assert (vault / "AI Workspace" / "my-project").is_dir()


def test_register_creates_knowledge_log(vault, cfg):
    reg = Registry(cfg)
    reg.register_project("my-project")
    log_path = vault / "AI Workspace" / "my-project" / "knowledge-log.md"
    assert log_path.exists()


def test_log_appends_to_knowledge_log(vault, cfg):
    reg = Registry(cfg)
    reg.register_project("my-project")
    reg.log("my-project", "Discovered that auth uses JWT")
    log_path = vault / "AI Workspace" / "my-project" / "knowledge-log.md"
    content = log_path.read_text()
    assert "Discovered that auth uses JWT" in content


def test_recall_returns_log_content(vault, cfg):
    reg = Registry(cfg)
    reg.register_project("my-project")
    reg.log("my-project", "Key insight here")
    result = reg.recall("my-project")
    assert "Key insight here" in result["content"]


def test_status_lists_projects(vault, cfg):
    reg = Registry(cfg)
    reg.register_project("alpha")
    reg.register_project("beta")
    status = reg.status()
    assert "alpha" in status["projects"]
    assert "beta" in status["projects"]


def test_add_note_to_project(vault, cfg):
    reg = Registry(cfg)
    reg.register_project("my-project")
    reg.add_note("my-project", "AI Workspace/my-project/arch.md")
    data = json.loads((vault / "AI Workspace" / "registry.json").read_text())
    assert "AI Workspace/my-project/arch.md" in data["projects"]["my-project"]["notes"]


def test_add_canvas_to_project(vault, cfg):
    reg = Registry(cfg)
    reg.register_project("my-project")
    reg.add_canvas("my-project", "AI Workspace/my-project/overview.canvas")
    data = json.loads((vault / "AI Workspace" / "registry.json").read_text())
    assert "AI Workspace/my-project/overview.canvas" in data["projects"]["my-project"]["canvases"]


def test_register_is_idempotent(vault, cfg):
    reg = Registry(cfg)
    reg.register_project("my-project")
    data_before = json.loads((vault / "AI Workspace" / "registry.json").read_text())
    reg.register_project("my-project")
    data_after = json.loads((vault / "AI Workspace" / "registry.json").read_text())
    assert data_before["projects"]["my-project"]["registered"] == data_after["projects"]["my-project"]["registered"]
    log_content = (vault / "AI Workspace" / "my-project" / "knowledge-log.md").read_text()
    assert log_content.count("# Knowledge Log") == 1


def test_log_returns_error_for_unregistered_project(vault, cfg):
    reg = Registry(cfg)
    result = reg.log("nonexistent", "some text")
    assert result["error"] is True
    assert "nonexistent" in result["message"]


def test_recall_returns_error_for_unregistered_project(vault, cfg):
    reg = Registry(cfg)
    result = reg.recall("nonexistent")
    assert result["error"] is True
