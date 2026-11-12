import os
from pathlib import Path
from typing import Dict, Any, Optional
import yaml

class ConfigLoader:
    def __init__(self, base_dir: Optional[str] = None):
        self.project_root = Path(base_dir) if base_dir else Path.cwd()
        self.config_dir = self.project_root / "config"
        self._settings_cache: Optional[Dict[str, Any]] = None
        self._biquote_cache: Optional[Dict[str, Any]] = None

    def _read_yaml(self, file_path: Path) -> Dict[str, Any]:
        if not file_path.exists():
            return {}
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                return yaml.safe_load(f) or {}
        except UnicodeDecodeError:
            with open(file_path, "r", encoding="utf-16") as f:
                return yaml.safe_load(f) or {}

    def get_settings(self) -> Dict[str, Any]:
        if self._settings_cache is None:
            settings_path = self.config_dir / "settings.yaml"
            data = self._read_yaml(settings_path)
            if not data:
                data = {
                    "project": {"symbol": "XAU/USD", "timezone": "UTC"},
                    "data_directory": "./data",
                    "default_output_format": "parquet",
                    "logging": {"level": "INFO", "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
                }
            self._settings_cache = data
        return self._settings_cache

    def get_biquote_config(self) -> Dict[str, Any]:
        if self._biquote_cache is None:
            biquote_path = self.config_dir / "biquote.yaml"
            data = self._read_yaml(biquote_path)
            if not data or "api" not in data:
                data = {
                    "api": {
                        "base_url": "https://biquote.io/api",
                        "timeout": 30,
                        "retry_count": 3,
                        "retry_delay": 1,
                        "rate_limit_per_minute": 15000
                    },
                    "symbol": "XAU/USD",
                    "supported_timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
                }
            else:
                # Ensure base_url has biquote.io
                if "base_url" in data.get("api", {}) and "api.biquote.io/v1" in data["api"]["base_url"]:
                    data["api"]["base_url"] = "https://biquote.io/api"
            self._biquote_cache = data
        return self._biquote_cache

    def resolve_path(self, rel_path: str) -> Path:
        path = Path(rel_path)
        if path.is_absolute():
            return path
        return self.project_root / path
