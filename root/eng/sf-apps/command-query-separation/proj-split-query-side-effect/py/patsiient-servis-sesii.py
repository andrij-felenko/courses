class SessionService:
    def __init__(self, log: Logger, store: ConfigStore) -> None:
        self._hits = 0                     # лічильник звернень «для метрик»
        self._config: Config | None = None # лінивий кеш конфігурації
        self._sessions: dict[str, Session] = {}
        self._log = log
        self._store = store

    # «get» у назві — а всередині МІНЯЄ лічильник і ще й пише в журнал
    def get_session(self, id: str) -> Session | None:
        self._hits += 1                                   # ← прихована зміна
        self._log.info(f"session lookup #{self._hits}: {id}")  # ← ще ефект
        return self._sessions.get(id)

    # теж «get» — а при першому виклику ЧИТАЄ з диска й КЕШУЄ
    def get_config(self) -> Config:
        if self._config is None:
            self._config = self._store.load()             # ← прихована зміна
        return self._config
