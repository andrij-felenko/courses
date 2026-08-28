# Python: подвійна перевірка на threading.Lock.
# Читання dict без замка безпечне під GIL; присвоєння атомарне — тож ідіом коректний.
import threading

class LoggerRegistry:
    def __init__(self):
        self._loggers: dict[str, Logger] = {}
        self._lock = threading.Lock()

    def get(self, name: str) -> "Logger":
        lg = self._loggers.get(name)      # швидка перевірка без замка
        if lg is not None:
            return lg
        with self._lock:                  # у вузьке місце — по одному
            lg = self._loggers.get(name)  # друга перевірка вже під замком
            if lg is None:
                lg = Logger(name)
                self._loggers[name] = lg
            return lg
