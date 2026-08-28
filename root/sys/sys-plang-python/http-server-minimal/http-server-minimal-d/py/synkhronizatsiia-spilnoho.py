import threading
import time

class ThreadSafeTelemetryRegistry:
    """Потокобезпечний реєстр телеметрії з гранулярним блокуванням."""
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._records: dict[str, dict] = {}
        self._request_counter = 0

    def register_metric(self, sensor_id: str, value: float) -> None:
        with self._lock:
            self._request_counter += 1
            self._records[sensor_id] = {
                "val": value,
                "ts": time.time()
            }

    def get_aggregated_snapshot(self) -> dict:
        with self._lock:
            # Створюємо поверхневу копію словника для безпечної серіалізації в JSON
            # без блокування реєстру на час відправки даних у мережу
            return {
                "total_processed": self._request_counter,
                "sensors": dict(self._records)
            }
