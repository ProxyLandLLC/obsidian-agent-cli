import json
from pathlib import Path
from unittest.mock import patch
from obsidian_cli.config import Config, load_config, save_config

def test_load_config_returns_defaults_when_no_file(tmp_path):
    with patch("obsidian_cli.config.CONFIG_FILE", tmp_path / "config.json"), \
         patch("obsidian_cli.config.ENV_FILE", tmp_path / ".env"):
        cfg = load_config()
    assert cfg.vault_path == ""
    assert cfg.api_url == "http://127.0.0.1:27123"
    assert cfg.workspace_path == "AI Workspace"
    assert cfg.teach_path == "AI Workspace/Teaching Notes"

def test_save_and_load_config(tmp_path):
    cfg = Config(
        vault_path="/my/vault",
        workspace_path="AI Workspace",
        teach_path="AI Workspace/Teaching Notes",
        api_url="http://127.0.0.1:27123",
        api_key="secret123",
        api_verify_ssl=False,
    )
    config_file = tmp_path / "config.json"
    env_file = tmp_path / ".env"
    with patch("obsidian_cli.config.CONFIG_FILE", config_file), \
         patch("obsidian_cli.config.ENV_FILE", env_file), \
         patch("obsidian_cli.config.CONFIG_DIR", tmp_path):
        save_config(cfg)
        loaded = load_config()
    assert loaded.vault_path == "/my/vault"
    assert loaded.api_key == "secret123"

def test_api_key_not_in_config_json(tmp_path):
    cfg = Config(vault_path="/v", api_key="topsecret")
    config_file = tmp_path / "config.json"
    env_file = tmp_path / ".env"
    with patch("obsidian_cli.config.CONFIG_FILE", config_file), \
         patch("obsidian_cli.config.ENV_FILE", env_file), \
         patch("obsidian_cli.config.CONFIG_DIR", tmp_path):
        save_config(cfg)
        data = json.loads(config_file.read_text())
    assert "api_key" not in data

def test_clearing_api_key_removes_env_file(tmp_path):
    cfg_with_key = Config(vault_path="/v", api_key="mykey")
    cfg_no_key = Config(vault_path="/v", api_key="")
    config_file = tmp_path / "config.json"
    env_file = tmp_path / ".env"
    with patch("obsidian_cli.config.CONFIG_FILE", config_file), \
         patch("obsidian_cli.config.ENV_FILE", env_file), \
         patch("obsidian_cli.config.CONFIG_DIR", tmp_path):
        save_config(cfg_with_key)
        assert env_file.exists()
        save_config(cfg_no_key)
        assert not env_file.exists()
