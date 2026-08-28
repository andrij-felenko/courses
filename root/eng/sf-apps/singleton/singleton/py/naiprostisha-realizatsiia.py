class Config:
    _instance = None                  # єдиний екземпляр

    def __init__(self):
        self._settings = load_from_disk()   # дорога робота — читаємо файл

    @classmethod
    def get_instance(cls):
        if cls._instance is None:     # ще нема — створюємо
            cls._instance = cls()
        return cls._instance          # завжди той самий об'єкт

    def get(self, key):
        return self._settings.get(key)

# будь-де в програмі:
db_host = Config.get_instance().get("db.host")
