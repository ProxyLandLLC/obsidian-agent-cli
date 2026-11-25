import json
from datetime import date, datetime
from pathlib import Path
from .config import Config, validate_folder


class Registry:
    def __init__(self, config: Config):
        self.config = config
        self._registry_path = Path(config.vault_path) / config.workspace_path / "registry.json"

    def _load(self) -> dict:
        if self._registry_path.exists():
            data = json.loads(self._registry_path.read_text(encoding="utf-8"))
            if data.get("schema_version") != 2 or not isinstance(data.get("projects"), dict):
                raise ValueError("Unsupported registry format; select a fresh workspace name")
            return data
        return {"schema_version": 2, "projects": {}}

    def _save(self, data: dict) -> None:
        self._registry_path.parent.mkdir(parents=True, exist_ok=True)
        self._registry_path.write_text(json.dumps(data, indent=2), encoding="utf-8")

    def _project_dir(self, name: str) -> Path:
        validate_folder(name)
        return Path(self.config.vault_path) / self.config.projects_path / name

    def _log_path(self, name: str) -> Path:
        return self._project_dir(name) / "knowledge-log.md"

    def register_project(self, name: str) -> dict:
        validate_folder(name)
        data = self._load()
        if name not in data["projects"]:
            data["projects"][name] = {
                "registered": str(date.today()),
                "path": f"{self.config.projects_path}/{name}",
                "notes": [],
                "canvases": [],
                "log": f"{self.config.projects_path}/{name}/knowledge-log.md",
            }
            self._save(data)
        proj_dir = self._project_dir(name)
        proj_dir.mkdir(parents=True, exist_ok=True)
        log = self._log_path(name)
        if not log.exists():
            log.write_text(f"# Knowledge Log — {name}\n\n", encoding="utf-8")
        return {"ok": True, "project": name}

    def log(self, project: str, text: str) -> dict:
        data = self._load()
        if project not in data["projects"]:
            return {"error": True, "message": f"Project '{project}' not found. Run: obsidian-agent workspace project register {project}"}
        log = self._log_path(project)
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
        entry = f"\n## {timestamp}\n{text}\n"
        with open(log, "a", encoding="utf-8") as f:
            f.write(entry)
        return {"ok": True, "project": project, "logged": text}

    def recall(self, project: str) -> dict:
        data = self._load()
        if project not in data["projects"]:
            return {"error": True, "message": f"Project '{project}' not found"}
        log = self._log_path(project)
        content = log.read_text(encoding="utf-8") if log.exists() else ""
        proj = data["projects"][project]
        return {
            "project": project,
            "content": content,
            "notes": proj.get("notes", []),
            "canvases": proj.get("canvases", []),
        }

    def status(self) -> dict:
        data = self._load()
        summary = {}
        for name, proj in data["projects"].items():
            summary[name] = {
                "registered": proj.get("registered"),
                "note_count": len(proj.get("notes", [])),
                "canvas_count": len(proj.get("canvases", [])),
                "path": proj.get("path"),
            }
        return {"projects": summary}

    def add_note(self, project: str, note_path: str) -> dict:
        data = self._load()
        if project not in data["projects"]:
            return {"error": True, "message": f"Project '{project}' not registered"}
        if note_path not in data["projects"][project]["notes"]:
            data["projects"][project]["notes"].append(note_path)
        self._save(data)
        return {"ok": True}

    def add_canvas(self, project: str, canvas_path: str) -> dict:
        data = self._load()
        if project not in data["projects"]:
            return {"error": True, "message": f"Project '{project}' not registered"}
        if canvas_path not in data["projects"][project]["canvases"]:
            data["projects"][project]["canvases"].append(canvas_path)
        self._save(data)
        return {"ok": True}
