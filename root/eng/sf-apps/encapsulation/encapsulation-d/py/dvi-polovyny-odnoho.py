class Account:
    def __init__(self) -> None:
        self._balance = 0        # приховане за домовленістю (підкреслення)

    def deposit(self, sum: int) -> None:
        if sum <= 0:
            raise ValueError("сума має бути додатною")
        self._balance += sum

    def withdraw(self, sum: int) -> None:
        if sum <= 0:
            raise ValueError("сума має бути додатною")
        if sum > self._balance:
            raise ValueError("недостатньо коштів")   # інваріант під захистом
        self._balance -= sum

    @property
    def amount(self) -> int:     # лише читання
        return self._balance
