from typing import Protocol, Union

Leaf = Union[str, int, bool, dict]        # dict тут — лише мітка {"secret": "..."}

def is_ref(v: Leaf) -> bool:
    # Секрет упізнаємо ЗА ФОРМОЮ: словник з єдиним ключем `secret`.
    return isinstance(v, dict) and set(v) == {"secret"}

# Той самий поділ, що в статті: горішні — конфіг, долішні — секрети.
manifest: dict[str, Leaf] = {
    "mqtt_url":    "mqtts://broker.dh.internal:8883",   # конфіг
    "poll_sec":    30,                                  # конфіг
    "log_level":   "info",                              # конфіг
    "db_host":     "prod-db.internal",                  # конфіг
    "db_password": {"secret": "dh/db/password"},        # СЕКРЕТ — лише адреса у сховищі
    "cloud_token": {"secret": "dh/cloud/hub-token"},    # СЕКРЕТ — лише адреса у сховищі
}
