import json
import os
from datetime import date, datetime, timedelta
from typing import Any, Dict, List, Optional

import requests


class TBADataDownloader:
    def __init__(self, base_url: str, headers: Dict[str, str], cache_dir: str = "cachedResponses") -> None:
        self.base_url = base_url.rstrip("/")
        self.headers = headers
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def _cache_path(self, name: str) -> str:
        filename = f"{name}.json"
        return os.path.join(self.cache_dir, filename)

    def _load_cache(self, name: str) -> Optional[Any]:
        path = self._cache_path(name)
        if not os.path.exists(path):
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (OSError, json.JSONDecodeError):
            return None

    def _save_cache(self, name: str, data: Any) -> None:
        path = self._cache_path(name)
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(data, f)
        except OSError:
            # If caching fails, just skip; network result is still usable.
            pass

    def get_completed_event_keys(self, year: int, today: Optional[date] = None) -> List[str]:
        """
        Return event keys for events whose end_date is at least one full day in the past.
        i.e., end_date <= (today - 1 day).
        """
        if today is None:
            today = date.today()
        cutoff = today - timedelta(days=1)

        print(f"Fetching {year} events from TBA...")
        try:
            resp = requests.get(f"{self.base_url}/events/{year}", headers=self.headers)
        except requests.RequestException as e:
            print(f"Warning: failed to fetch events for {year}: {e}")
            return []

        if resp.status_code != 200:
            print(f"Warning: failed to fetch events for {year}, status code {resp.status_code}")
            return []

        events = resp.json()

        keys: List[str] = []
        for event in events:
            end_date_str = event.get("end_date")
            key = event.get("key")
            if not key:
                continue

            # Cache each event individually as its own JSON file
            self._save_cache(f"event_{key}", event)

            if not end_date_str:
                continue

            try:
                end = datetime.strptime(end_date_str, "%Y-%m-%d").date()
            except ValueError:
                continue
            if end <= cutoff:
                keys.append(key)

        return keys

    def get_event_matches(self, event_key: str) -> List[dict]:
        cache_key = f"matches_{event_key}"
        cached = self._load_cache(cache_key)
        if cached is not None:
            return cached

        print(f"Fetching matches for event {event_key} from TBA...")
        try:
            resp = requests.get(f"{self.base_url}/event/{event_key}/matches", headers=self.headers)
        except requests.RequestException as e:
            print(f"Warning: failed to fetch matches for event {event_key}: {e}")
            return []

        if resp.status_code != 200:
            print(f"Warning: failed to fetch matches for event {event_key}, status code {resp.status_code}")
            return []

        data = resp.json()
        self._save_cache(cache_key, data)
        return data

