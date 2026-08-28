import threading
from typing import Dict, Optional, NamedTuple

class CacheEntry(NamedTuple):
    value: str
    version: int

class DistributedCache:
    def __init__(self):
        self._entries: Dict[str, CacheEntry] = {}
        self._lock = threading.Lock()

    def get(self, key: str) -> Optional[CacheEntry]:
        with self._lock:
            return self._entries.get(key)

    def put_if_newer(self, key: str, value: str, version: int) -> bool:
        with self._lock:
            existing = self._entries.get(key)
            if existing and existing.version >= version:
                print(f"[Py Cache Guard] Stale write rejected for '{key}': "
                      f"Current v{existing.version} >= Incoming v{version}")
                return False
            self._entries[key] = CacheEntry(value, version)
            print(f"[Py Cache] Updated '{key}' to v{version}")
            return True

    def evict(self, key: str) -> None:
        with self._lock:
            if self._entries.pop(key, None):
                print(f"[Py Evict] Key '{key}' removed from cache.")

# Демонстрація роботи харнесу
if __name__ == "__main__":
    cache = DistributedCache()
    cache.put_if_newer("user_42", "Kyiv Main St", version=1)
    cache.evict("user_42")
    cache.put_if_newer("user_42", "Fresh Lviv St", version=2)
    cache.put_if_newer("user_42", "Stale St", version=1) # Відхилено!
