from dataclasses import dataclass
from datetime import datetime

@dataclass(frozen=True)
class Money:
    cents: int
    ccy: str

@dataclass(frozen=True)
class Payment:
    id: int
    amount: Money
    created_at: datetime
    def settle(self) -> None: ...

@dataclass(frozen=True)
class CardPayment(Payment):
    card_last4: str
    auth_code: str
    def settle(self) -> None: ...      # провести через платіжний шлюз

@dataclass(frozen=True)
class BankTransfer(Payment):
    iban: str
    reference: str
    def settle(self) -> None: ...      # звірити з банківською випискою
