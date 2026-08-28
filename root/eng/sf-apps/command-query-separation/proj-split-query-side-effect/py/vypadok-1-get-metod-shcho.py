class SessionService:
    def __init__(self) -> None:
        self._hits = 0
        self._sessions: dict[str, Session] = {}

    # ЗАПИТ: лише повертає, стан не чіпає. Клич скільки хоч.
    def get_session(self, id: str) -> Session | None:
        return self._sessions.get(id)

    # КОМАНДА: явно реєструє перегляд. Нічого не повертає.
    def record_session_view(self, id: str) -> None:
        self._hits += 1

    # ЗАПИТ на саму метрику — теж чистий.
    def view_count(self) -> int:
        return self._hits
