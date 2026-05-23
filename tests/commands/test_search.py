import json
import pytest
from click.testing import CliRunner
from unittest.mock import patch, MagicMock
from obsidian_cli.commands.search import search
from obsidian_cli.config import Config


@pytest.fixture
def cfg():
    return Config(vault_path="/vault", api_url="http://127.0.0.1:27123", api_key="test")


def run_search(cfg, *args, transport_attrs=None):
    runner = CliRunner()
    with patch("obsidian_cli.commands.search.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.search.Transport") as MockTransport:
        t = MagicMock()
        t.search_simple.return_value = {"results": [], "transport": "api"}
        t.get_tags.return_value = {"tags": {"python": 3}, "transport": "api"}
        t.search_advanced.return_value = {"results": [], "transport": "api"}
        if transport_attrs:
            for k, v in transport_attrs.items():
                getattr(t, k).return_value = v
        MockTransport.return_value = t
        result = runner.invoke(search, list(args))
    return result


def test_search_simple_outputs_json(cfg):
    result = run_search(cfg, "simple", "python",
                        transport_attrs={"search_simple": {"results": [{"filename": "note.md"}], "transport": "api"}})
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert out["results"][0]["filename"] == "note.md"


def test_search_tags_outputs_json(cfg):
    result = run_search(cfg, "tags")
    assert result.exit_code == 0
    out = json.loads(result.output)
    assert "tags" in out


def test_search_advanced_calls_dql(cfg):
    runner = CliRunner()
    with patch("obsidian_cli.commands.search.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.search.Transport") as MockTransport:
        t = MagicMock()
        t.search_advanced.return_value = {"results": [], "transport": "api"}
        MockTransport.return_value = t
        result = runner.invoke(search, ["advanced", "TABLE file.name FROM \"Chief\""])
    assert result.exit_code == 0
    t.search_advanced.assert_called_once_with(
        "TABLE file.name FROM \"Chief\"",
        "application/vnd.olrapi.dataview.dql+txt"
    )


def test_search_jsonlogic_calls_transport(cfg):
    runner = CliRunner()
    with patch("obsidian_cli.commands.search.load_config", return_value=cfg), \
         patch("obsidian_cli.commands.search.Transport") as MockTransport:
        t = MagicMock()
        t.search_advanced.return_value = {"results": [], "transport": "api"}
        MockTransport.return_value = t
        result = runner.invoke(search, ["jsonlogic", "{\"==\": [{\"var\": \"type\"}, \"note\"]}"])
    assert result.exit_code == 0
    t.search_advanced.assert_called_once_with(
        "{\"==\": [{\"var\": \"type\"}, \"note\"]}",
        "application/vnd.olrapi.jsonlogic+json"
    )
