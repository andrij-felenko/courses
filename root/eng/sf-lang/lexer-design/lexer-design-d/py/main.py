from dataclasses import dataclass, field
from enum import Enum, auto


class Kind(Enum):
    NUM = auto(); IDENT = auto(); PLUS = auto(); MINUS = auto()
    STAR = auto(); LPAREN = auto(); RPAREN = auto(); END = auto()


@dataclass
class Token:
    kind: Kind
    value: int = 0        # для NUM — розібране число
    text: str = ""        # для IDENT — саме ім'я (лексема)


class Lexer:
    def __init__(self, src: str):
        self.src = src
        self.pos = 0       # поточна позиція у вхідному тексті

    def _peek(self) -> str:
        return self.src[self.pos] if self.pos < len(self.src) else "\0"

    def next(self) -> Token:
        while self._peek().isspace():          # 1) проковтнути пробіли
            self.pos += 1

        if self._peek() == "\0":               # кінець вводу
            return Token(Kind.END)

        if self._peek().isdigit():             # 2) НАЙДОВШЕ число
            v = 0
            while self._peek().isdigit():      # тягнемо цифри, доки йдуть
                v = v * 10 + (ord(self.src[self.pos]) - ord("0"))  # рахуємо значення
                self.pos += 1
            return Token(Kind.NUM, value=v)

        if self._peek().isalpha():             # 3) НАЙДОВШЕ ім'я
            start = self.pos
            while self._peek().isalnum():      # тягнемо буквоцифри
                self.pos += 1
            return Token(Kind.IDENT, text=self.src[start:self.pos])  # (ключові слова — нижче)

        ch = self.src[self.pos]                # 4) односимвольні оператори й дужки
        self.pos += 1
        singles = {"+": Kind.PLUS, "-": Kind.MINUS, "*": Kind.STAR,
                   "(": Kind.LPAREN, ")": Kind.RPAREN}
        return Token(singles.get(ch, Kind.END))  # невідомий символ — тут спрощено
