"""
Data loading utilities — reads CSV, JSON, or plain text sources.
"""
import csv
import json
import logging
from pathlib import Path
from typing import List, Dict, Any, Optional

from app.config import Config
from app.utils.helpers import chunk_list

logger = logging.getLogger(__name__)


class DataLoader:
    """Load datasets from various file formats."""

    def __init__(self, config: Config, base_dir: Optional[Path] = None):
        self.config = config
        self.base_dir = base_dir or Path(__file__).resolve().parent

    def load_csv(self, filename: str, delimiter: str = ",") -> List[Dict[str, str]]:
        """Load a CSV file and return a list of row dictionaries."""
        filepath = self.base_dir / filename
        rows = []
        try:
            with open(filepath, newline="", encoding="utf-8") as f:
                reader = csv.DictReader(f, delimiter=delimiter)
                for row in reader:
                    rows.append(dict(row))
            logger.info(f"Loaded {len(rows)} rows from {filepath}")
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
        return rows

    def load_json(self, filename: str) -> Any:
        """Load a JSON file and return the parsed object."""
        filepath = self.base_dir / filename
        try:
            with open(filepath, encoding="utf-8") as f:
                data = json.load(f)
            logger.info(f"Loaded JSON from {filepath}")
            return data
        except (FileNotFoundError, json.JSONDecodeError) as e:
            logger.error(f"Failed to load JSON {filepath}: {e}")
            return None

    def load_text_lines(self, filename: str) -> List[str]:
        """Read a plain text file and return non-empty lines."""
        filepath = self.base_dir / filename
        try:
            with open(filepath, encoding="utf-8") as f:
                lines = [line.strip() for line in f if line.strip()]
            logger.info(f"Loaded {len(lines)} lines from {filepath}")
            return lines
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            return []

    def load_in_batches(self, filename: str, batch_size: int = 100) -> List[List[Dict]]:
        """Load a CSV and return it split into batches."""
        rows = self.load_csv(filename)
        return chunk_list(rows, batch_size)
