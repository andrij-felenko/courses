# config.py — весь файл виконається один раз, при першому import цього модуля

class _Config:
    def __init__(self):
        self._settings = load_from_disk()    # дорога робота, робиться один раз

    def get(self, key):
        return self._settings.get(key)


config = _Config()        # створюється при першому імпорті config.py


# деінде в програмі:
#   from config import config
#   config.get("db.host")
