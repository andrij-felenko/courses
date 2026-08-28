import threading

class Config:
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:            # швидка перевірка без замка
            with cls._lock:                  # у вузьке місце — по одному
                if cls._instance is None:    # друга перевірка вже під замком
                    inst = super().__new__(cls)
                    inst._settings = load_from_disk()
                    cls._instance = inst     # публікуємо ГОТОВИМ, останнім кроком
        return cls._instance
