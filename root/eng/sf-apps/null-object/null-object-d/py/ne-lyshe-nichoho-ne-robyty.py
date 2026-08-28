class Customer(Protocol):
    def name(self) -> str: ...
    def discount_rate(self) -> float: ...

class RegularCustomer:
    def __init__(self, name: str, rate: float) -> None:
        self._name, self._rate = name, rate
    def name(self) -> str: return self._name
    def discount_rate(self) -> float: return self._rate

class NullCustomer:
    def name(self) -> str: return "Гість"       # нейтральне ім'я
    def discount_rate(self) -> float: return 0.0  # жодної знижки

def find_customer(cid: str) -> Customer:
    return db.lookup(cid) or NullCustomer()      # ніколи не None
