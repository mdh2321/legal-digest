"""Persistent deadline tracker that accumulates across digest runs."""
import json
from datetime import datetime
from pathlib import Path
from typing import List, Dict


class DeadlineTracker:
    """Stores and manages compliance deadlines across runs."""

    def __init__(self, data_dir: str = "data"):
        """
        Initialize the deadline tracker.

        Args:
            data_dir: Directory to store deadlines.json
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.data_dir / "deadlines.json"
        self.deadlines = self._load()

    def _load(self) -> List[Dict]:
        """Load deadlines from JSON file."""
        if not self.file_path.exists():
            return []

        try:
            with open(self.file_path, 'r') as f:
                raw = json.load(f)
            # Parse date strings back to datetime for comparison
            for d in raw:
                if isinstance(d.get('date'), str):
                    d['date_obj'] = datetime.strptime(d['date'], '%Y-%m-%d')
            return raw
        except (json.JSONDecodeError, KeyError):
            return []

    def _save(self):
        """Save deadlines to JSON file."""
        # Store dates as strings for JSON serialization
        serializable = []
        for d in self.deadlines:
            entry = {k: v for k, v in d.items() if k != 'date_obj'}
            serializable.append(entry)

        with open(self.file_path, 'w') as f:
            json.dump(serializable, f, indent=2, default=str)

    def merge_new_deadlines(self, new_deadlines: List[Dict]):
        """
        Merge new deadlines into the persistent store.
        Deduplicates by date + jurisdiction + description similarity.

        Args:
            new_deadlines: List of deadline dicts from content_enhancer.extract_deadlines_from_stories
        """
        for nd in new_deadlines:
            date_str = nd.get('date_str') or nd['date'].strftime('%Y-%m-%d') if isinstance(nd['date'], datetime) else str(nd['date'])
            date_obj = nd['date'] if isinstance(nd['date'], datetime) else datetime.strptime(date_str, '%Y-%m-%d')

            # Check for duplicates
            is_duplicate = False
            for existing in self.deadlines:
                if (existing.get('date') == date_str and
                        existing.get('jurisdiction') == nd.get('jurisdiction')):
                    is_duplicate = True
                    break

            if not is_duplicate:
                self.deadlines.append({
                    'date': date_str,
                    'date_obj': date_obj,
                    'jurisdiction': nd.get('jurisdiction', ''),
                    'description': nd.get('description', ''),
                    'story_title': nd.get('story_title', ''),
                    'url': nd.get('url', ''),
                })

    def remove_past_deadlines(self):
        """Remove deadlines that have already passed."""
        now = datetime.now()
        self.deadlines = [
            d for d in self.deadlines
            if d.get('date_obj', datetime.min) >= now
        ]

    def get_all_upcoming(self) -> List[Dict]:
        """
        Get all upcoming deadlines sorted by date.

        Returns:
            List of deadline dicts with 'date' as datetime objects for display.
        """
        self.remove_past_deadlines()

        # Sort by date
        sorted_deadlines = sorted(
            self.deadlines,
            key=lambda d: d.get('date_obj', datetime.max)
        )

        # Convert date_obj back to 'date' key as datetime for compatibility
        # with the RSS generator's _format_compliance_countdown
        result = []
        for d in sorted_deadlines:
            result.append({
                'date': d.get('date_obj', datetime.now()),
                'date_str': d.get('date', ''),
                'description': d.get('description', ''),
                'jurisdiction': d.get('jurisdiction', ''),
                'story_title': d.get('story_title', ''),
                'url': d.get('url', ''),
            })

        return result

    def update(self, new_deadlines: List[Dict]):
        """
        Full update cycle: merge new, remove past, save.

        Args:
            new_deadlines: New deadlines from this week's digest
        """
        self.merge_new_deadlines(new_deadlines)
        self.remove_past_deadlines()
        self._save()
