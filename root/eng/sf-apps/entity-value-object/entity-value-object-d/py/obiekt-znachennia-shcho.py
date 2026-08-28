import re
from dataclasses import dataclass

_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")

@dataclass(frozen=True)
class Email:
    value: str

    def __post_init__(self):
        # dataclass кличе це одразу після створення — місце для перевірки інваріанта
        norm = self.value.strip().lower()
        if not _RE.match(norm):
            raise ValueError(f"не email: {self.value}")
        object.__setattr__(self, "value", norm)   # frozen — тож так записуємо нормалізоване

def send_welcome(to: Email) -> None:
    ...   # тут перевіряти НЕ треба: тип Email == уже валідний і нормалізований

Email("  Ivan@Example.COM ")   # ок → зберігає "ivan@example.com"
Email("привіт")                # ValueError одразу, а не колись у глибині системи
