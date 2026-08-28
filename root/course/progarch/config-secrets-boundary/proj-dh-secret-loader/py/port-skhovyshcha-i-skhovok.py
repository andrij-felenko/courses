class SecretStore(Protocol):
    def get(self, name: str) -> str: ...       # кидає, якщо секрета нема

REDACTED = "‹secret›"

class Secret:
    __slots__ = ("_value",)                    # без __dict__ — важче ненароком серіалізувати
    def __init__(self, value: str) -> None:
        self._value = value

    def expose(self) -> str:                   # ЄДИНИЙ навмисний вихід значення
        return self._value

    def __repr__(self) -> str:                 # repr(), логер, f"{s!r}"
        return REDACTED
    __str__ = __repr__                         # str(), f"{s}", print
    # json.dumps(Secret(...)) без default= КИНЕ TypeError — тобто НЕ виллє, а зупинить.
