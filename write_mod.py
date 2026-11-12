import base64, os

os.makedirs("C:/Users/ASUS/Desktop/gold_chart/src", exist_ok=True)

content = b"""import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional

class ConfigLoader:
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path.cwd()
        self._config_cache = {}

    def load_settings(self):
        settings_path = os.path.join(self.base_dir, "config", "settings.yaml")
        if settings not in self._config_cache:
            if settings_path.exists():
                with open(settings_path) as f:
                    self._config_cache = yaml.safe_load(f)
            else:
                self._config_cache = self._get_default_settings()
        return self._config_cache

    def _get_default_settings(self):
        return {
            project: {"symbol": "XAU/USD", "timezone": "UTC"},
            data_directory: "./data",
            default_output_format: "parquet",
            logging: {"level": "INFO", "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s"}
        }
"""

with open("C:/Users/ASUS/Desktop/gold_chart/src/config_loader.py", "wb") as f:
    f.write(content)

print("config_loader.py written")

