import json
from pathlib import Path
from typing import Dict, Any, List

class JsonLogger:
    """Manages atomic JSON exports for trading records and audits."""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

    def write_json(self, filename: str, data: List[Dict[str, Any]] | Dict[str, Any]):
        file_path = self.data_dir / filename
        tmp_path = file_path.with_suffix(".tmp")
        with open(tmp_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, default=str)
        tmp_path.replace(file_path)

    def read_json(self, filename: str) -> List[Dict[str, Any]] | Dict[str, Any]:
        file_path = self.data_dir / filename
        if not file_path.exists():
            return []
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
