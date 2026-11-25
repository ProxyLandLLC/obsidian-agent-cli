import json
import re
from dataclasses import dataclass, asdict, fields
from pathlib import Path

CONFIG_DIR = Path.home() / ".obsidian-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENV_FILE = CONFIG_DIR / ".env"

FOLDER_FIELDS = ("workspace_path", "raw_folder", "inbox_folder", "projects_folder", "reference_folder")


def validate_folder(name: str) -> str:
    """Accept a portable, single directory name, never a path."""
    if (not name or name != name.strip() or name.endswith(".")
            or name.startswith(".") or re.search(r'[<>:"/\\|?*\x00-\x1f]', name)
            or name.split(".")[0].upper() in {
                "CON", "PRN", "AUX", "NUL",
                *(f"COM{i}" for i in range(1, 10)),
                *(f"LPT{i}" for i in range(1, 10)),
            }):
        raise ValueError(f"Invalid folder name: {name!r}")
    return name


@dataclass
class Config:
    vault_path: str = ""
    workspace_path: str = "AI Workspace"
    raw_folder: str = "Raw"
    inbox_folder: str = "Inbox"
    projects_folder: str = "Projects"
    reference_folder: str = "Reference"
    api_url: str = "http://127.0.0.1:27123"
    api_key: str = ""
    api_verify_ssl: bool = False

    def __post_init__(self):
        self.validate_layout()

    def validate_layout(self):
        for key in FOLDER_FIELDS:
            validate_folder(getattr(self, key))
        names = [getattr(self, key).casefold() for key in FOLDER_FIELDS[1:]]
        if len(names) != len(set(names)) or "registry.json" in names:
            raise ValueError("Workspace subfolder names must be distinct and cannot be registry.json")

    @property
    def raw_path(self):
        return f"{self.workspace_path}/{self.raw_folder}"

    @property
    def inbox_path(self):
        return f"{self.workspace_path}/{self.inbox_folder}"

    @property
    def projects_path(self):
        return f"{self.workspace_path}/{self.projects_folder}"

    @property
    def reference_path(self):
        return f"{self.workspace_path}/{self.reference_folder}"

    def initialize_workspace(self):
        """Provision directories and a new-format registry without replacing files."""
        self.validate_layout()
        if not self.vault_path or not Path(self.vault_path).expanduser().is_dir():
            raise ValueError("Select an existing vault directory")
        vault = Path(self.vault_path).expanduser().resolve()
        self.vault_path = str(vault)
        workspace = vault / self.workspace_path
        locations = [workspace, *(vault / p for p in (
            self.raw_path, self.inbox_path, self.projects_path, self.reference_path
        ))]
        registry = workspace / "registry.json"
        for p in [*locations, registry]:
            if p.is_symlink() or not p.resolve().is_relative_to(vault):
                raise ValueError("Workspace paths must remain inside the vault and cannot be symlinks")
        for p in locations:
            if p.exists() and not p.is_dir():
                raise ValueError(f"Folder conflicts with an existing file: {p}")
        if registry.exists():
            data = json.loads(registry.read_text(encoding="utf-8"))
            if data.get("schema_version") != 2 or not isinstance(data.get("projects"), dict):
                raise ValueError("Unsupported registry format; select a fresh workspace name")
        for p in locations:
            p.mkdir(parents=True, exist_ok=True)
        if not registry.exists():
            with registry.open("x", encoding="utf-8") as f:
                json.dump({"schema_version": 2, "projects": {}}, f, indent=2)
        return [str(p.relative_to(vault).as_posix()) for p in locations]

def load_config() -> Config:
    data: dict = {}
    if CONFIG_FILE.exists():
        data = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    if ENV_FILE.exists():
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            if line.startswith("OBSIDIAN_API_KEY="):
                data["api_key"] = line.split("=", 1)[1].strip()
    valid_keys = {f.name for f in fields(Config)}
    return Config(**{k: v for k, v in data.items() if k in valid_keys})


def save_config(config: Config) -> None:
    config.validate_layout()
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    data = asdict(config)
    api_key = data.pop("api_key", "")
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    if api_key:
        ENV_FILE.write_text(f"OBSIDIAN_API_KEY={api_key}\n", encoding="utf-8")
    elif ENV_FILE.exists():
        ENV_FILE.unlink()
