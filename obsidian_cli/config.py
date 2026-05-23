import json
from dataclasses import dataclass, asdict, fields
from pathlib import Path

CONFIG_DIR = Path.home() / ".obsidian-cli"
CONFIG_FILE = CONFIG_DIR / "config.json"
ENV_FILE = CONFIG_DIR / ".env"


@dataclass
class Config:
    vault_path: str = ""
    workspace_path: str = "AI Workspace"
    teach_path: str = "AI Workspace/Teaching Notes"
    api_url: str = "http://127.0.0.1:27123"
    api_key: str = ""
    api_verify_ssl: bool = False


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
    CONFIG_DIR.mkdir(exist_ok=True)
    data = asdict(config)
    api_key = data.pop("api_key", "")
    CONFIG_FILE.write_text(json.dumps(data, indent=2), encoding="utf-8")
    if api_key:
        ENV_FILE.write_text(f"OBSIDIAN_API_KEY={api_key}\n", encoding="utf-8")
    elif ENV_FILE.exists():
        ENV_FILE.unlink()
