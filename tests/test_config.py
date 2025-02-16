import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from dotenv import load_dotenv
from src.utils import load_config
import pytest

@pytest.fixture(autouse=True)
def setup_env():
    """自動設置環境"""
    load_dotenv()
    yield

def test_config_structure():
    """測試設定檔結構"""
    config = load_config()
    assert "bot" in config
    assert "prefix" in config["bot"]
    assert "status" in config["bot"]

def test_environment_variables():
    """測試環境變數載入"""
    assert os.getenv("DISCORD_TOKEN") is not None
    assert os.getenv("BOT_PREFIX") == "!"

def test_config_defaults():
    """測試預設值"""
    config = load_config()
    assert config["bot"]["prefix"] == "!"
    assert "Minecraft" in config["bot"]["status"] 