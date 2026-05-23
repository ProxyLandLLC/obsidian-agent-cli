import json
import pytest
from click.testing import CliRunner
from pathlib import Path
from unittest.mock import patch, MagicMock
from obsidian_cli.commands.note import note
from obsidian_cli.config import Config
from obsidian_cli.transport import Transport


@pytest.fixture
def vault(tmp_path):
    (tmp_path / "AI Workspace").mkdir()
    return tmp_path


@pytest.fixture
def cfg(vault):
    return Config(vault_path=str(vault), workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


def make_runner(cfg):
    """Return a function that runs note subcommands with FS-only transport."""
    def run(*args):
        runner = CliRunner()
        real_transport = Transport(cfg)
        real_transport._api_available = False
        with patch("obsidian_cli.commands.note.load_config", return_value=cfg), \
             patch("obsidian_cli.commands.note.Transport", return_value=real_transport):
            return runner.invoke(note, list(args))
    return run


def test_note_create(vault, cfg):
    run = make_runner(cfg)
    result = run("create", "AI Workspace/hello.md", "--content", "# Hello")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["ok"] is True
    assert (vault / "AI Workspace" / "hello.md").read_text(encoding="utf-8") == "# Hello"


def test_note_read(vault, cfg):
    (vault / "AI Workspace" / "existing.md").write_text("# Existing", encoding="utf-8")
    run = make_runner(cfg)
    result = run("read", "AI Workspace/existing.md")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["content"] == "# Existing"


def test_note_delete(vault, cfg):
    note_path = vault / "AI Workspace" / "del.md"
    note_path.write_text("bye", encoding="utf-8")
    run = make_runner(cfg)
    result = run("delete", "AI Workspace/del.md")
    assert result.exit_code == 0
    assert not note_path.exists()


def test_note_list(vault, cfg):
    (vault / "AI Workspace" / "a.md").write_text("a", encoding="utf-8")
    (vault / "AI Workspace" / "b.md").write_text("b", encoding="utf-8")
    run = make_runner(cfg)
    result = run("list", "AI Workspace")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert "a.md" in out["files"]


def test_note_update_append(vault, cfg):
    (vault / "AI Workspace" / "log.md").write_text("Existing content", encoding="utf-8")
    run = make_runner(cfg)
    result = run("update", "AI Workspace/log.md", "New line", "--append")
    assert result.exit_code == 0
    content = (vault / "AI Workspace" / "log.md").read_text(encoding="utf-8")
    assert "Existing content" in content
    assert "New line" in content
    assert content.index("Existing content") < content.index("New line")


def test_note_update_append_error_on_missing(vault, cfg):
    run = make_runner(cfg)
    result = run("update", "AI Workspace/missing.md", "content", "--append")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["error"] is True


def test_note_meta_full(vault, cfg):
    runner = CliRunner()
    meta_data = {
        "path": "AI Workspace/note.md",
        "content": "# Note",
        "frontmatter": {"status": "active"},
        "tags": ["project"],
        "stat": {"ctime": 0, "mtime": 0, "size": 6},
        "transport": "api",
    }
    mock_t = MagicMock()
    mock_t.get_note_meta.return_value = meta_data
    with patch("obsidian_cli.commands.note.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.note.Transport", return_value=mock_t):
        result = CliRunner().invoke(note, ["meta", "AI Workspace/note.md"])
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["frontmatter"]["status"] == "active"


def test_note_meta_frontmatter_flag(vault, cfg):
    runner = CliRunner()
    meta_data = {"frontmatter": {"status": "active"}, "tags": [], "stat": {}, "transport": "api"}
    mock_t = MagicMock()
    mock_t.get_note_meta.return_value = meta_data
    with patch("obsidian_cli.commands.note.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.note.Transport", return_value=mock_t):
        result = runner.invoke(note, ["meta", "AI Workspace/note.md", "--frontmatter"])
    out = json.loads(result.output)
    assert "frontmatter" in out
    assert "tags" not in out


def test_note_map(vault, cfg):
    runner = CliRunner()
    map_data = {"headings": [{"heading": "Intro", "level": 1}], "blocks": [], "frontmatterFields": ["status"], "transport": "api"}
    mock_t = MagicMock()
    mock_t.get_note_map.return_value = map_data
    with patch("obsidian_cli.commands.note.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.note.Transport", return_value=mock_t):
        result = runner.invoke(note, ["map", "AI Workspace/note.md"])
    out = json.loads(result.output)
    assert out["headings"][0]["heading"] == "Intro"


def test_note_patch_create_if_missing_flag(vault, cfg):
    runner = CliRunner()
    mock_t = MagicMock()
    mock_t.patch_file.return_value = {"ok": True, "transport": "api"}
    with patch("obsidian_cli.commands.note.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.note.Transport", return_value=mock_t):
        result = runner.invoke(note, [
            "patch", "AI Workspace/note.md", "value",
            "--target", "status",
            "--target-type", "frontmatter",
            "--operation", "replace",
            "--create-if-missing",
        ])
    assert result.exit_code == 0
    mock_t.patch_file.assert_called_once_with(
        "AI Workspace/note.md", "value", "replace", "frontmatter", "status",
        True, False, False
    )


_DQL = "application/vnd.olrapi.dataview.dql+txt"


def test_note_backlinks(vault, cfg):
    runner = CliRunner()
    mock_t = MagicMock()
    mock_t.search_advanced.return_value = {"results": [], "transport": "api"}
    with patch("obsidian_cli.commands.note.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.note.Transport", return_value=mock_t):
        result = runner.invoke(note, ["backlinks", "AI Workspace/my-note.md"])
    assert result.exit_code == 0
    mock_t.search_advanced.assert_called_once_with("LIST FROM [[my-note]]", _DQL)


def test_note_recent_default_limit(vault, cfg):
    runner = CliRunner()
    mock_t = MagicMock()
    mock_t.search_advanced.return_value = {"results": [], "transport": "api"}
    with patch("obsidian_cli.commands.note.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.note.Transport", return_value=mock_t):
        result = runner.invoke(note, ["recent"])
    assert result.exit_code == 0
    call_args = mock_t.search_advanced.call_args[0]
    assert "LIMIT 10" in call_args[0]


def test_note_by_tag_strips_hash(vault, cfg):
    runner = CliRunner()
    mock_t = MagicMock()
    mock_t.search_advanced.return_value = {"results": [], "transport": "api"}
    with patch("obsidian_cli.commands.note.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.note.Transport", return_value=mock_t):
        result = runner.invoke(note, ["by-tag", "#project"])
    assert result.exit_code == 0
    call_args = mock_t.search_advanced.call_args[0]
    assert "FROM #project" in call_args[0]


def test_note_orphans(vault, cfg):
    runner = CliRunner()
    mock_t = MagicMock()
    mock_t.search_advanced.return_value = {"results": [], "transport": "api"}
    with patch("obsidian_cli.commands.note.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.note.Transport", return_value=mock_t):
        result = runner.invoke(note, ["orphans"])
    assert result.exit_code == 0
    call_args = mock_t.search_advanced.call_args[0]
    assert "inlinks" in call_args[0]
