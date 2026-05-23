import json
import pytest
from pathlib import Path
from unittest.mock import MagicMock, patch
from obsidian_cli.config import Config
from obsidian_cli.transport import Transport


@pytest.fixture
def vault(tmp_path):
    (tmp_path / "AI Workspace").mkdir()
    return tmp_path


@pytest.fixture
def cfg(vault):
    return Config(vault_path=str(vault), api_url="http://127.0.0.1:27123", api_key="test")


@pytest.fixture
def transport_no_api(cfg):
    t = Transport(cfg)
    t._api_available = False
    return t


def test_is_api_available_false_on_connection_error(cfg):
    t = Transport(cfg)
    with patch.object(t.session, "get", side_effect=Exception("refused")):
        assert t.is_api_available() is False


def test_read_note_fs_fallback(transport_no_api, vault):
    note = vault / "AI Workspace" / "test.md"
    note.write_text("# Hello", encoding="utf-8")
    result = transport_no_api.read_file("AI Workspace/test.md")
    assert result["content"] == "# Hello"
    assert result["transport"] == "fs"


def test_write_note_fs_fallback(transport_no_api, vault):
    result = transport_no_api.write_file("AI Workspace/new.md", "# New Note")
    assert result["ok"] is True
    assert result["transport"] == "fs"
    assert (vault / "AI Workspace" / "new.md").read_text(encoding="utf-8") == "# New Note"


def test_delete_note_fs_fallback(transport_no_api, vault):
    note = vault / "AI Workspace" / "del.md"
    note.write_text("bye", encoding="utf-8")
    result = transport_no_api.delete_file("AI Workspace/del.md")
    assert result["ok"] is True
    assert result["transport"] == "fs"
    assert not note.exists()


def test_list_files_fs_fallback(transport_no_api, vault):
    (vault / "AI Workspace" / "a.md").write_text("a", encoding="utf-8")
    (vault / "AI Workspace" / "b.md").write_text("b", encoding="utf-8")
    result = transport_no_api.list_files("AI Workspace")
    assert "a.md" in result["files"]
    assert "b.md" in result["files"]
    assert result["transport"] == "fs"


def test_build_patch_headers_minimal(cfg):
    t = Transport(cfg)
    h = t._build_patch_headers("append", "heading", "Introduction")
    assert h["Operation"] == "append"
    assert h["Target-Type"] == "heading"
    assert h["Target"] == "Introduction"
    assert "Create-Target-If-Missing" not in h


def test_build_patch_headers_all_flags(cfg):
    t = Transport(cfg)
    h = t._build_patch_headers("replace", "frontmatter", "status",
                                create_if_missing=True,
                                apply_if_preexists=True,
                                trim_whitespace=True)
    assert h["Create-Target-If-Missing"] == "true"
    assert h["Apply-If-Content-Preexists"] == "true"
    assert h["Trim-Target-Whitespace"] == "true"


def test_get_note_meta_requires_api(cfg):
    t = Transport(cfg)
    t._api_available = False
    result = t.get_note_meta("AI Workspace/note.md")
    assert result["error"] is True


def test_get_note_map_requires_api(cfg):
    t = Transport(cfg)
    t._api_available = False
    result = t.get_note_map("AI Workspace/note.md")
    assert result["error"] is True


def test_get_server_status_requires_api(cfg):
    t = Transport(cfg)
    t._api_available = False
    result = t.get_server_status()
    assert result["error"] is True


def test_get_note_meta_sends_accept_header(cfg):
    t = Transport(cfg)
    t._api_available = True
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"path": "AI Workspace/note.md", "content": "# Hi", "frontmatter": {}, "tags": [], "stat": {}}
    with patch.object(t.session, "get", return_value=mock_resp) as mock_get:
        t.get_note_meta("AI Workspace/note.md")
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["headers"]["Accept"] == "application/vnd.olrapi.note+json"


def test_get_note_map_sends_accept_header(cfg):
    t = Transport(cfg)
    t._api_available = True
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"headings": [], "blocks": [], "frontmatterFields": []}
    with patch.object(t.session, "get", return_value=mock_resp) as mock_get:
        t.get_note_map("AI Workspace/note.md")
        call_kwargs = mock_get.call_args[1]
        assert call_kwargs["headers"]["Accept"] == "application/vnd.olrapi.document-map+json"


def test_write_periodic_requires_api(cfg):
    t = Transport(cfg)
    t._api_available = False
    assert t.write_periodic("daily", "content")["error"] is True


def test_append_periodic_requires_api(cfg):
    t = Transport(cfg)
    t._api_available = False
    assert t.append_periodic("daily", "content")["error"] is True


def test_delete_periodic_requires_api(cfg):
    t = Transport(cfg)
    t._api_available = False
    assert t.delete_periodic("daily")["error"] is True


def test_get_periodic_date_requires_api(cfg):
    t = Transport(cfg)
    t._api_available = False
    assert t.get_periodic_date("daily", 2026, 5, 11)["error"] is True


def test_write_periodic_uses_put(cfg):
    t = Transport(cfg)
    t._api_available = True
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    with patch.object(t.session, "put", return_value=mock_resp) as mock_put:
        t.write_periodic("daily", "# Today")
        mock_put.assert_called_once()
        assert "/periodic/daily/" in mock_put.call_args[0][0]


def test_append_periodic_uses_post(cfg):
    t = Transport(cfg)
    t._api_available = True
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    with patch.object(t.session, "post", return_value=mock_resp) as mock_post:
        t.append_periodic("daily", "new line")
        mock_post.assert_called_once()
        assert "/periodic/daily/" in mock_post.call_args[0][0]


def test_get_periodic_date_url_format(cfg):
    t = Transport(cfg)
    t._api_available = True
    mock_resp = MagicMock()
    mock_resp.text = "content"
    mock_resp.raise_for_status = MagicMock()
    with patch.object(t.session, "get", return_value=mock_resp) as mock_get:
        t.get_periodic_date("daily", 2026, 5, 3)
        url = mock_get.call_args[0][0]
        assert "/periodic/daily/2026/05/03/" in url


def test_write_active_requires_api(cfg):
    t = Transport(cfg)
    t._api_available = False
    assert t.write_active("content")["error"] is True


def test_append_active_requires_api(cfg):
    t = Transport(cfg)
    t._api_available = False
    assert t.append_active("content")["error"] is True


def test_delete_active_requires_api(cfg):
    t = Transport(cfg)
    t._api_available = False
    assert t.delete_active()["error"] is True


def test_get_active_meta_sends_accept_header(cfg):
    t = Transport(cfg)
    t._api_available = True
    mock_resp = MagicMock()
    mock_resp.json.return_value = {"content": "", "frontmatter": {}, "tags": [], "stat": {}}
    with patch.object(t.session, "get", return_value=mock_resp) as mock_get:
        t.get_active_meta()
        assert mock_get.call_args[1]["headers"]["Accept"] == "application/vnd.olrapi.note+json"


def test_write_active_uses_put(cfg):
    t = Transport(cfg)
    t._api_available = True
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    with patch.object(t.session, "put", return_value=mock_resp) as mock_put:
        t.write_active("# New content")
        assert "/active/" in mock_put.call_args[0][0]


def test_patch_file_no_api_returns_error(cfg):
    t = Transport(cfg)
    t._api_available = False
    result = t.patch_file("note.md", "text", "append", "heading", "Intro")
    assert result["error"] is True
    assert result["transport"] == "fs"


def test_patch_file_api_sends_headers(cfg):
    t = Transport(cfg)
    t._api_available = True
    mock_resp = MagicMock()
    mock_resp.raise_for_status = MagicMock()
    with patch.object(t.session, "patch", return_value=mock_resp) as mock_patch:
        t.patch_file("note.md", "hello", "append", "heading", "Intro", create_if_missing=True)
    _, kwargs = mock_patch.call_args
    assert kwargs["headers"]["Operation"] == "append"
    assert kwargs["headers"]["Create-Target-If-Missing"] == "true"


def test_move_file_fs(transport_no_api, vault):
    src = vault / "AI Workspace" / "src.md"
    src.write_text("# Source", encoding="utf-8")
    result = transport_no_api.move_file("AI Workspace/src.md", "AI Workspace/dest.md")
    assert result["ok"] is True
    assert not src.exists()
    assert (vault / "AI Workspace" / "dest.md").read_text(encoding="utf-8") == "# Source"


def test_move_file_missing_src(transport_no_api, vault):
    result = transport_no_api.move_file("AI Workspace/missing.md", "AI Workspace/dest.md")
    assert result["error"] is True


def test_rename_tag_in_vault(cfg, vault):
    note = vault / "AI Workspace" / "note.md"
    note.write_text("tags: []\n\nI use #todo everywhere", encoding="utf-8")
    t = Transport(cfg)
    result = t.rename_tag_in_vault("#todo", "#task")
    assert result["changed_count"] == 1
    assert "#task" in note.read_text(encoding="utf-8")


def test_rename_tag_dry_run(cfg, vault):
    note = vault / "AI Workspace" / "note.md"
    original = "I use #todo here"
    note.write_text(original, encoding="utf-8")
    t = Transport(cfg)
    result = t.rename_tag_in_vault("#todo", "#task", dry_run=True)
    assert result["changed_count"] == 1
    assert result["dry_run"] is True
    assert note.read_text(encoding="utf-8") == original
