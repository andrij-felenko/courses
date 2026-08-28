  # config.py — весь модуль виконається один раз при першому import
  class _Config:
      def __init__(self):
          self._settings = load_from_disk()
      def get(self, key):
          return self._settings.get(key)

  config = _Config()        # створюється при першому імпорті цього модуля

  # деінде:  from config import config;  config.get("db.host")
