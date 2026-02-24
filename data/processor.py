"""
Data processing and transformation utilities.
"""
import logging
import statistics
from typing import List, Dict, Any, Optional, Callable

from app.utils.helpers import deep_merge
from app.utils.validators import sanitize_string

logger = logging.getLogger(__name__)


class DataProcessor:
    """Transform, clean, and aggregate raw data records."""

    def __init__(self):
        self._pipeline: List[Callable[[List[Dict]], List[Dict]]] = []

    # ------------------------------------------------------------------ #
    # Pipeline builder
    # ------------------------------------------------------------------ #

    def add_step(self, fn: Callable[[List[Dict]], List[Dict]]) -> "DataProcessor":
        """Add a transformation step to the pipeline."""
        self._pipeline.append(fn)
        return self

    def run(self, data: List[Dict]) -> List[Dict]:
        """Execute all pipeline steps in order."""
        result = data
        for step in self._pipeline:
            result = step(result)
            logger.debug(f"After step '{step.__name__}': {len(result)} records")
        return result

    # ------------------------------------------------------------------ #
    # Built-in transformations
    # ------------------------------------------------------------------ #

    @staticmethod
    def drop_missing(records: List[Dict], required_keys: List[str]) -> List[Dict]:
        """Remove records that are missing any required key or have empty values."""
        cleaned = [
            r for r in records
            if all(r.get(k) not in (None, "", []) for k in required_keys)
        ]
        logger.info(f"drop_missing: kept {len(cleaned)}/{len(records)} records")
        return cleaned

    @staticmethod
    def normalize_strings(records: List[Dict], fields: List[str]) -> List[Dict]:
        """Strip and lower-case specified string fields."""
        for record in records:
            for field in fields:
                if field in record and isinstance(record[field], str):
                    record[field] = sanitize_string(record[field]).lower()
        return records

    @staticmethod
    def cast_numeric(records: List[Dict], fields: List[str]) -> List[Dict]:
        """Cast specified fields to float, dropping records where conversion fails."""
        result = []
        for record in records:
            try:
                for field in fields:
                    record[field] = float(record[field])
                result.append(record)
            except (ValueError, KeyError):
                logger.warning(f"Skipping record due to cast failure: {record}")
        return result

    @staticmethod
    def compute_stats(records: List[Dict], numeric_field: str) -> Dict[str, Any]:
        """Compute basic descriptive statistics for a numeric field."""
        values = [r[numeric_field] for r in records if numeric_field in r]
        if not values:
            return {}
        return {
            "count": len(values),
            "mean": statistics.mean(values),
            "median": statistics.median(values),
            "stdev": statistics.stdev(values) if len(values) > 1 else 0,
            "min": min(values),
            "max": max(values),
        }

    @staticmethod
    def group_by(records: List[Dict], key: str) -> Dict[str, List[Dict]]:
        """Group records by the value of a specific key."""
        groups: Dict[str, List[Dict]] = {}
        for record in records:
            group_key = str(record.get(key, "unknown"))
            groups.setdefault(group_key, []).append(record)
        return groups

    @staticmethod
    def merge_defaults(records: List[Dict], defaults: Dict) -> List[Dict]:
        """Apply default values to each record for any missing keys."""
        return [deep_merge(defaults, record) for record in records]
