from typing import Optional, Protocol

BASIC = {"export-csv"}                    # що дозволено на вільному тарифі

class Subscription(Protocol):
    def price(self) -> float: ...
    def storage_gb(self) -> int: ...
    def seats(self) -> int: ...
    def includes(self, feature: str) -> bool: ...

class Account:
    def __init__(self, name: str, sub: Optional[Subscription]) -> None:
        self.name = name
        self._sub = sub                   # вільні користувачі: None

    def monthly_price(self) -> float:
        if self._sub is not None:
            return self._sub.price()
        return 0.0                        # вільний тариф

    def storage_gb(self) -> int:
        if self._sub is not None:
            return self._sub.storage_gb()
        return 1                          # вільний тариф: 1 ГБ

    def seats(self) -> int:
        if self._sub is not None:
            return self._sub.seats()
        return 1

    def has_feature(self, f: str) -> bool:
        if self._sub is not None:
            return self._sub.includes(f)
        return f in BASIC
