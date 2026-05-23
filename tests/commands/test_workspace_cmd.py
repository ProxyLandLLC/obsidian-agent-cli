import json
import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch
from obsidian_cli.commands.workspace_cmd import workspace
from obsidian_cli.config import Config


@pytest.fixture
def vault(tmp_path):
    (tmp_path / "AI Workspace").mkdir()
    return tmp_path


@pytest.fixture
def cfg(vault):
    return Config(vault_path=str(vault), workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


def make_runner(cfg):
    def run(*args):
        runner = CliRunner()
        with patch("obsidian_cli.commands.workspace_cmd.load_config", return_value=cfg):
            return runner.invoke(workspace, list(args))
    return run


def test_workspace_status_empty(vault, cfg):
    run = make_runner(cfg)
    result = run("status")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert "projects" in out


def test_workspace_project_register(vault, cfg):
    run = make_runner(cfg)
    result = run("project", "register", "my-app")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["ok"] is True
    assert (vault / "AI Workspace" / "my-app").is_dir()


def test_workspace_log(vault, cfg):
    run = make_runner(cfg)
    run("project", "register", "my-app")
    result = run("log", "my-app", "Uses PostgreSQL for persistence")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["ok"] is True
    log = (vault / "AI Workspace" / "my-app" / "knowledge-log.md").read_text()
    assert "Uses PostgreSQL for persistence" in log


def test_workspace_recall(vault, cfg):
    run = make_runner(cfg)
    run("project", "register", "my-app")
    run("log", "my-app", "Auth uses JWT")
    result = run("recall", "my-app")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert "Auth uses JWT" in out["content"]
