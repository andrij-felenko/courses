from abc import ABC

class Approver(ABC):
    def __init__(self) -> None:
        self._next: "Approver | None" = None

    def set_next(self, nxt: "Approver") -> "Approver":
        self._next = nxt
        return nxt                       # повертаємо наступного — зручно зчіплювати

    def handle(self, amount: float) -> None:
        if self._next:
            self._next.handle(amount)
        else:
            print(f"Нема кому погодити {amount}")


class TeamLead(Approver):
    def handle(self, amount: float) -> None:
        if amount <= 1_000:
            print(f"Керівник групи погодив {amount}")
        else:
            super().handle(amount)       # не моє — передаю далі


class Manager(Approver):
    def handle(self, amount: float) -> None:
        if amount <= 10_000:
            print(f"Начальник відділу погодив {amount}")
        else:
            super().handle(amount)


class Director(Approver):
    def handle(self, amount: float) -> None:
        if amount <= 100_000:
            print(f"Директор погодив {amount}")
        else:
            super().handle(amount)
