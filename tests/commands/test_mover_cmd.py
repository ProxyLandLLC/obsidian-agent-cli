import json
import pytest
from click.testing import CliRunner
from unittest.mock import MagicMock, patch
from obsidian_cli.commands.mover_cmd import mover_cmd, _match_rule
from obsidian_cli.config import Config


@pytest.fixture
def cfg():
    return Config(vault_path="/tmp/vault", workspace_path="AI Workspace",
                  api_url="http://127.0.0.1:27123", api_key="test")


RULES = [
    {"pattern": "#project", "folder": "Projects/"},
    {"pattern": "^meeting-", "folder": "Meetings/"},
]


def run_mover(cfg, mock_t, *args, rules=RULES):
    runner = CliRunner()
    with patch("obsidian_cli.commands.mover_cmd.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.mover_cmd.Transport", return_value=mock_t), \
         patch("obsidian_cli.commands.mover_cmd._load_mover_rules", return_value=rules):
        return runner.invoke(mover_cmd, list(args))


def test_list_rules(cfg):
    mock_t = MagicMock()
    result = run_mover(cfg, mock_t, "rules")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["count"] == 2


def test_check_note_tag_match(cfg):
    mock_t = MagicMock()
    mock_t.get_note_meta.return_value = {"tags": ["#project"], "transport": "api"}
    result = run_mover(cfg, mock_t, "check", "AI Workspace/my-note.md")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["matched"] is True
    assert data["folder"] == "Projects/"


def test_check_note_pattern_match(cfg):
    mock_t = MagicMock()
    mock_t.get_note_meta.return_value = {"tags": [], "transport": "api"}
    result = run_mover(cfg, mock_t, "check", "AI Workspace/meeting-2026.md")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["matched"] is True
    assert data["folder"] == "Meetings/"


def test_check_note_no_match(cfg):
    mock_t = MagicMock()
    mock_t.get_note_meta.return_value = {"tags": [], "transport": "api"}
    result = run_mover(cfg, mock_t, "check", "AI Workspace/random.md")
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["matched"] is False


def test_move_note(cfg):
    mock_t = MagicMock()
    mock_t.run_command.return_value = {"ok": True, "transport": "api"}
    result = run_mover(cfg, mock_t, "move", "AI Workspace/my-note.md")
    assert result.exit_code == 0
    mock_t.run_command.assert_called_once_with("auto-note-mover:move-file")
    data = json.loads(result.output)
    assert data["note"] == "AI Workspace/my-note.md"


def test_match_rule_tag():
    rules = [{"pattern": "#project", "folder": "Projects/"}]
    rule = _match_rule(rules, "my-note", ["#project"])
    assert rule is not None
    assert rule["folder"] == "Projects/"


def test_match_rule_regex():
    rules = [{"pattern": "^meeting-", "folder": "Meetings/"}]
    rule = _match_rule(rules, "meeting-2026", [])
    assert rule is not None


def test_match_rule_no_match():
    rules = [{"pattern": "#project", "folder": "Projects/"}]
    rule = _match_rule(rules, "random", [])
    assert rule is None
