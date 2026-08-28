from dataclasses import dataclass

@dataclass(frozen=True)          # frozen → поля не переприсвоїти після створення
class TempRange:
    min: float
    max: float
    def __post_init__(self) -> None:
        if self.min > self.max:   # перевірили ОДИН раз — і назавжди
            raise ValueError("min не може бути більший за max")
    # «Зміна» = новий обʼєкт, що знову проходить перевірку.
    def with_min(self, v: float) -> "TempRange":
        return TempRange(v, self.max)
