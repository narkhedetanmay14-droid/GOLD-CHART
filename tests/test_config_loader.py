import pytest
from pathlib import Path
import sys
import os

# Add src to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "src")))

from config_loader import ConfigLoader

def test_config_loader_init():
    loader = ConfigLoader()
    assert loader is not None
    assert loader.project_root.exists()

def test_config_loader_settings():
    loader = ConfigLoader()
    settings = loader.get_settings()
    assert isinstance(settings, dict)
    assert settings.get("project", {}).get("symbol") == "XAU/USD"
    assert settings.get("project", {}).get("timezone") == "UTC"

def test_config_loader_biquote():
    loader = ConfigLoader()
    biquote_cfg = loader.get_biquote_config()
    assert isinstance(biquote_cfg, dict)
    assert "api" in biquote_cfg
    assert "https://biquote.io/api" in biquote_cfg["api"]["base_url"]

def test_resolve_path():
    loader = ConfigLoader()
    resolved = loader.resolve_path("data/raw")
    assert isinstance(resolved, Path)
    assert str(resolved).endswith("data\\raw") or str(resolved).endswith("data/raw")
