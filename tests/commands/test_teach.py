import json
import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch
from obsidian_cli.commands.teach import teach
from obsidian_cli.config import Config
from obsidian_cli.transport import Transport


@pytest.fixture
def vault(tmp_path):
    teach_dir = tmp_path / "AI Workspace" / "Teaching Notes"
    teach_dir.mkdir(parents=True)
    return tmp_path


@pytest.fixture
def cfg(vault):
    return Config(vault_path=str(vault),
                  teach_path="AI Workspace/Teaching Notes",
                  api_url="http://127.0.0.1:27123", api_key="test")


def make_runner(cfg):
    def run(*args):
        runner = CliRunner()
        real_transport = Transport(cfg)
        real_transport._api_available = False
        with patch("obsidian_cli.commands.teach.load_config", return_value=cfg), \
             patch("obsidian_cli.commands.teach.Transport", return_value=real_transport):
            return runner.invoke(teach, list(args))
    return run


def test_teach_write_creates_note(vault, cfg):
    run = make_runner(cfg)
    result = run("write", "JWT Auth", "--content", "JWT stands for...")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["ok"] is True
    files = list((vault / "AI Workspace" / "Teaching Notes").glob("*.md"))
    assert len(files) == 1
    content = files[0].read_text(encoding="utf-8")
    assert "JWT stands for..." in content
    assert "# JWT Auth" in content


def test_teach_list(vault, cfg):
    (vault / "AI Workspace" / "Teaching Notes" / "topic.md").write_text("content", encoding="utf-8")
    run = make_runner(cfg)
    result = run("list")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert "topic.md" in out["files"]


def test_teach_write_slugifies_title(vault, cfg):
    run = make_runner(cfg)
    result = run("write", "How JWT Works!", "--content", "explanation")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert "how-jwt-works" in out["path"]
