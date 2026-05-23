from pathlib import Path
import requests
from .config import Config


class Transport:
    def __init__(self, config: Config):
        self.config = config
        self._api_available: bool | None = None
        self.session = requests.Session()
        self.session.headers["Authorization"] = f"Bearer {config.api_key}"
        self.session.verify = config.api_verify_ssl

    # ── API availability ──────────────────────────────────────────────────

    def is_api_available(self) -> bool:
        if self._api_available is not None:
            return self._api_available
        try:
            r = self.session.get(f"{self.config.api_url}/", timeout=2)
            self._api_available = r.status_code in (200, 401)
        except Exception:
            self._api_available = False
        return self._api_available

    def _safe_api(self, call) -> dict:
        try:
            return call()
        except Exception as e:
            return {"error": True, "message": str(e), "transport": "api"}

    # ── Unified public methods ────────────────────────────────────────────

    def read_file(self, vault_path: str) -> dict:
        if self.is_api_available():
            return self._api_read(vault_path)
        return self._fs_read(vault_path)

    def write_file(self, vault_path: str, content: str) -> dict:
        if self.is_api_available():
            return self._api_write(vault_path, content)
        return self._fs_write(vault_path, content)

    def delete_file(self, vault_path: str) -> dict:
        if self.is_api_available():
            return self._api_delete(vault_path)
        return self._fs_delete(vault_path)

    def list_files(self, folder: str = "") -> dict:
        if self.is_api_available():
            return self._api_list(folder)
        return self._fs_list(folder)

    def patch_file(self, vault_path: str, content: str,
                   operation: str, target_type: str, target: str,
                   create_if_missing: bool = False,
                   apply_if_preexists: bool = False,
                   trim_whitespace: bool = False) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "patch requires REST API (Obsidian must be running)", "transport": "fs"}
        def _call():
            return self._api_patch(vault_path, content, operation, target_type, target,
                                   create_if_missing, apply_if_preexists, trim_whitespace)
        return self._safe_api(_call)

    def search_simple(self, query: str) -> dict:
        if self.is_api_available():
            return self._api_search_simple(query)
        return {"error": True, "message": "search requires REST API (Obsidian must be running)", "transport": "fs"}

    def search_advanced(self, query: str, content_type: str) -> dict:
        if self.is_api_available():
            return self._api_search_advanced(query, content_type)
        return {"error": True, "message": "advanced search requires REST API", "transport": "fs"}

    def get_tags(self) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "tags require REST API", "transport": "fs"}
        def _call():
            r = self.session.get(f"{self.config.api_url}/tags/")
            r.raise_for_status()
            return {"tags": r.json(), "transport": "api"}
        return self._safe_api(_call)

    def move_file(self, src: str, dest: str) -> dict:
        """Move/rename a file. Uses read+write+delete since the REST API has no native move."""
        content_result = self.read_file(src)
        if "error" in content_result and content_result["error"]:
            return content_result
        write_result = self.write_file(dest, content_result["content"])
        if "error" in write_result and write_result["error"]:
            return write_result
        self.delete_file(src)
        transport = content_result.get("transport", "fs")
        return {"ok": True, "src": src, "dest": dest, "transport": transport}

    def rename_tag_in_vault(self, old_tag: str, new_tag: str, dry_run: bool = False) -> dict:
        """Rename a tag across all vault notes (filesystem scan + in-place replace)."""
        import re
        old_norm = old_tag if old_tag.startswith("#") else f"#{old_tag}"
        new_norm = new_tag if new_tag.startswith("#") else f"#{new_tag}"
        vault = Path(self.config.vault_path)
        changed = []
        pattern = re.compile(r"(?<!\w)" + re.escape(old_norm) + r"(?=\W|$)")
        for p in vault.rglob("*.md"):
            rel = p.relative_to(vault)
            if rel.parts[0] == ".obsidian":
                continue
            text = p.read_text(encoding="utf-8", errors="ignore")
            if pattern.search(text):
                changed.append(str(rel).replace("\\", "/"))
                if not dry_run:
                    new_text = pattern.sub(new_norm, text)
                    p.write_text(new_text, encoding="utf-8")
        return {
            "old_tag": old_norm,
            "new_tag": new_norm,
            "changed_count": len(changed),
            "changed": changed,
            "dry_run": dry_run,
            "transport": "fs",
        }

    def open_in_obsidian(self, vault_path: str) -> dict:
        import subprocess
        import sys
        vault_name = Path(self.config.vault_path).name
        uri = f"obsidian://open?vault={vault_name}&file={vault_path}"
        if sys.platform == "win32":
            subprocess.Popen(["cmd", "/c", "start", uri], shell=False)
        elif sys.platform == "darwin":
            subprocess.Popen(["open", uri])
        else:
            subprocess.Popen(["xdg-open", uri])
        return {"ok": True, "uri": uri, "transport": "uri"}

    def list_commands(self) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            r = self.session.get(f"{self.config.api_url}/commands/")
            r.raise_for_status()
            return {"commands": r.json(), "transport": "api"}
        return self._safe_api(_call)

    def run_command(self, command_id: str) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            r = self.session.post(f"{self.config.api_url}/commands/{command_id}/")
            r.raise_for_status()
            return {"ok": True, "command_id": command_id, "transport": "api"}
        return self._safe_api(_call)

    def get_periodic(self, period: str) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            r = self.session.get(f"{self.config.api_url}/periodic/{period}/")
            r.raise_for_status()
            return {"content": r.text, "transport": "api"}
        return self._safe_api(_call)

    def get_active(self) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            r = self.session.get(f"{self.config.api_url}/active/")
            r.raise_for_status()
            return {"content": r.text, "transport": "api"}
        return self._safe_api(_call)

    def get_active_meta(self) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            r = self.session.get(
                f"{self.config.api_url}/active/",
                headers={"Accept": "application/vnd.olrapi.note+json"},
            )
            r.raise_for_status()
            return {**r.json(), "transport": "api"}
        return self._safe_api(_call)

    def write_active(self, content: str) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            r = self.session.put(
                f"{self.config.api_url}/active/",
                data=content.encode(),
                headers={"Content-Type": "text/markdown"},
            )
            r.raise_for_status()
            return {"ok": True, "transport": "api"}
        return self._safe_api(_call)

    def append_active(self, content: str) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            r = self.session.post(
                f"{self.config.api_url}/active/",
                data=content.encode(),
                headers={"Content-Type": "text/markdown"},
            )
            r.raise_for_status()
            return {"ok": True, "transport": "api"}
        return self._safe_api(_call)

    def patch_active(self, content: str, operation: str, target_type: str, target: str,
                     create_if_missing: bool = False,
                     apply_if_preexists: bool = False,
                     trim_whitespace: bool = False) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            headers = self._build_patch_headers(operation, target_type, target,
                                                 create_if_missing, apply_if_preexists, trim_whitespace)
            r = self.session.patch(
                f"{self.config.api_url}/active/",
                data=content.encode(),
                headers=headers,
            )
            r.raise_for_status()
            return {"ok": True, "transport": "api"}
        return self._safe_api(_call)

    def delete_active(self) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            r = self.session.delete(f"{self.config.api_url}/active/")
            r.raise_for_status()
            return {"ok": True, "transport": "api"}
        return self._safe_api(_call)

    def get_note_meta(self, vault_path: str) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "note meta requires REST API", "transport": "fs"}
        def _call():
            r = self.session.get(
                f"{self.config.api_url}/vault/{vault_path}",
                headers={"Accept": "application/vnd.olrapi.note+json"},
            )
            r.raise_for_status()
            return {**r.json(), "transport": "api"}
        return self._safe_api(_call)

    def get_note_map(self, vault_path: str) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "note map requires REST API", "transport": "fs"}
        def _call():
            r = self.session.get(
                f"{self.config.api_url}/vault/{vault_path}",
                headers={"Accept": "application/vnd.olrapi.document-map+json"},
            )
            r.raise_for_status()
            return {**r.json(), "transport": "api"}
        return self._safe_api(_call)

    def get_server_status(self) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "Obsidian REST API is not available", "transport": "fs"}
        def _call():
            r = self.session.get(f"{self.config.api_url}/", timeout=2)
            r.raise_for_status()
            return {**r.json(), "transport": "api"}
        return self._safe_api(_call)

    def write_periodic(self, period: str, content: str) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            r = self.session.put(
                f"{self.config.api_url}/periodic/{period}/",
                data=content.encode(),
                headers={"Content-Type": "text/markdown"},
            )
            r.raise_for_status()
            return {"ok": True, "transport": "api"}
        return self._safe_api(_call)

    def append_periodic(self, period: str, content: str) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            r = self.session.post(
                f"{self.config.api_url}/periodic/{period}/",
                data=content.encode(),
                headers={"Content-Type": "text/markdown"},
            )
            r.raise_for_status()
            return {"ok": True, "transport": "api"}
        return self._safe_api(_call)

    def patch_periodic(self, period: str, content: str,
                       operation: str, target_type: str, target: str,
                       create_if_missing: bool = False,
                       apply_if_preexists: bool = False,
                       trim_whitespace: bool = False) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            headers = self._build_patch_headers(operation, target_type, target,
                                                 create_if_missing, apply_if_preexists, trim_whitespace)
            r = self.session.patch(
                f"{self.config.api_url}/periodic/{period}/",
                data=content.encode(),
                headers=headers,
            )
            r.raise_for_status()
            return {"ok": True, "transport": "api"}
        return self._safe_api(_call)

    def delete_periodic(self, period: str) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            r = self.session.delete(f"{self.config.api_url}/periodic/{period}/")
            r.raise_for_status()
            return {"ok": True, "transport": "api"}
        return self._safe_api(_call)

    def get_periodic_date(self, period: str, year: int, month: int, day: int) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            r = self.session.get(
                f"{self.config.api_url}/periodic/{period}/{year}/{month:02d}/{day:02d}/")
            r.raise_for_status()
            return {"content": r.text, "transport": "api"}
        return self._safe_api(_call)

    def write_periodic_date(self, period: str, year: int, month: int, day: int, content: str) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            r = self.session.put(
                f"{self.config.api_url}/periodic/{period}/{year}/{month:02d}/{day:02d}/",
                data=content.encode(),
                headers={"Content-Type": "text/markdown"},
            )
            r.raise_for_status()
            return {"ok": True, "transport": "api"}
        return self._safe_api(_call)

    def append_periodic_date(self, period: str, year: int, month: int, day: int, content: str) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            r = self.session.post(
                f"{self.config.api_url}/periodic/{period}/{year}/{month:02d}/{day:02d}/",
                data=content.encode(),
                headers={"Content-Type": "text/markdown"},
            )
            r.raise_for_status()
            return {"ok": True, "transport": "api"}
        return self._safe_api(_call)

    def delete_periodic_date(self, period: str, year: int, month: int, day: int) -> dict:
        if not self.is_api_available():
            return {"error": True, "message": "requires REST API", "transport": "fs"}
        def _call():
            r = self.session.delete(
                f"{self.config.api_url}/periodic/{period}/{year}/{month:02d}/{day:02d}/")
            r.raise_for_status()
            return {"ok": True, "transport": "api"}
        return self._safe_api(_call)

    # ── REST API internals ────────────────────────────────────────────────

    def _api_read(self, vault_path: str) -> dict:
        r = self.session.get(f"{self.config.api_url}/vault/{vault_path}")
        r.raise_for_status()
        return {"content": r.text, "transport": "api"}

    def _api_write(self, vault_path: str, content: str) -> dict:
        r = self.session.put(
            f"{self.config.api_url}/vault/{vault_path}",
            data=content.encode(),
            headers={"Content-Type": "text/markdown"},
        )
        r.raise_for_status()
        return {"ok": True, "transport": "api"}

    def _api_delete(self, vault_path: str) -> dict:
        r = self.session.delete(f"{self.config.api_url}/vault/{vault_path}")
        r.raise_for_status()
        return {"ok": True, "transport": "api"}

    def _api_list(self, folder: str) -> dict:
        path = f"{self.config.api_url}/vault/{folder}/" if folder else f"{self.config.api_url}/vault/"
        r = self.session.get(path)
        r.raise_for_status()
        data = r.json()
        return {"files": data.get("files", []), "transport": "api"}

    def _build_patch_headers(self, operation: str, target_type: str, target: str,
                              create_if_missing: bool = False,
                              apply_if_preexists: bool = False,
                              trim_whitespace: bool = False) -> dict:
        headers = {
            "Content-Type": "text/plain",
            "Operation": operation,
            "Target-Type": target_type,
            "Target": target,
        }
        if create_if_missing:
            headers["Create-Target-If-Missing"] = "true"
        if apply_if_preexists:
            headers["Apply-If-Content-Preexists"] = "true"
        if trim_whitespace:
            headers["Trim-Target-Whitespace"] = "true"
        return headers

    def _api_patch(self, vault_path: str, content: str,
                   operation: str, target_type: str, target: str,
                   create_if_missing: bool = False,
                   apply_if_preexists: bool = False,
                   trim_whitespace: bool = False) -> dict:
        headers = self._build_patch_headers(operation, target_type, target,
                                             create_if_missing, apply_if_preexists, trim_whitespace)
        r = self.session.patch(
            f"{self.config.api_url}/vault/{vault_path}",
            data=content.encode(),
            headers=headers,
        )
        r.raise_for_status()
        return {"ok": True, "transport": "api"}

    def _api_search_simple(self, query: str) -> dict:
        r = self.session.post(
            f"{self.config.api_url}/search/simple/",
            params={"query": query},
        )
        r.raise_for_status()
        return {"results": r.json(), "transport": "api"}

    def _api_search_advanced(self, query: str, content_type: str) -> dict:
        r = self.session.post(
            f"{self.config.api_url}/search/",
            data=query.encode(),
            headers={"Content-Type": content_type},
        )
        r.raise_for_status()
        return {"results": r.json(), "transport": "api"}

    # ── File system internals ─────────────────────────────────────────────

    def _abs(self, vault_path: str) -> Path:
        return Path(self.config.vault_path) / vault_path

    def _fs_read(self, vault_path: str) -> dict:
        p = self._abs(vault_path)
        if not p.exists():
            return {"error": True, "message": f"Not found: {vault_path}", "transport": "fs"}
        return {"content": p.read_text(encoding="utf-8"), "transport": "fs"}

    def _fs_write(self, vault_path: str, content: str) -> dict:
        p = self._abs(vault_path)
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        return {"ok": True, "path": vault_path, "transport": "fs"}

    def _fs_delete(self, vault_path: str) -> dict:
        p = self._abs(vault_path)
        if not p.exists():
            return {"error": True, "message": f"Not found: {vault_path}", "transport": "fs"}
        p.unlink()
        return {"ok": True, "transport": "fs"}

    def _fs_list(self, folder: str) -> dict:
        p = self._abs(folder) if folder else Path(self.config.vault_path)
        if not p.exists():
            return {"error": True, "message": f"Folder not found: {folder}", "transport": "fs"}
        # Returns filenames only (not full paths), consistent with API response shape
        files = [f.name for f in p.iterdir()]
        return {"files": files, "transport": "fs"}
