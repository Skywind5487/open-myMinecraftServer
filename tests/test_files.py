from pathlib import Path
import json
import contextlib

def test_config_json_exists():
    """測試設定檔存在性"""
    config_path = Path("assets/config.json")
    assert config_path.exists()

def test_config_json_format():
    """測試設定檔格式"""
    with open("assets/config.json", "r", encoding="utf-8") as f:
        config = json.load(f)
    assert isinstance(config, dict)
    assert "bot" in config

def test_wiki_files():
    """測試 wiki 檔案結構"""
    wiki_path = Path("assets/wiki")
    assert wiki_path.exists()
    assert (wiki_path / "首頁.md").exists() 