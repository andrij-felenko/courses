import signal, threading, logging
log = logging.getLogger("dh.config")

class Config:
    def __init__(self, m, store, initial):
        self._m, self._store = m, store
        self._snapshot = initial               # незмінний знімок
        self._lock = threading.Lock()          # single-flight

    @classmethod
    def load(cls, m, store) -> "Config":
        # СТАРТ: fail-closed. Немає секрета — застосунок НЕ піднімається (resolve кине).
        return cls(m, store, resolve(m, store))

    def snapshot(self) -> dict[str, object]:
        return self._snapshot                  # читач бере ВЕСЬ знімок за раз

    def reload(self) -> None:
        # РОТАЦІЯ: single-flight (неблокувальний acquire) + fail-static.
        if not self._lock.acquire(blocking=False):
            return                             # вже йде перечит — не громадимо стадо
        try:
            try:
                nxt = resolve(self._m, self._store)
            except Exception as err:
                log.warning("secret reload failed, keeping snapshot: %s", err)
                return                         # fail-static: лишаємось на робочому знімку
            self._snapshot = nxt               # атомна підміна посилання (під GIL)
        finally:
            self._lock.release()
