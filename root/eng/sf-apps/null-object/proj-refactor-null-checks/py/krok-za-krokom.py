FREE: Subscription = FreeSubscription()   # спільний, про нього — нижче

class Account:
    def __init__(self, name: str, sub: Subscription) -> None:
        self.name = name
        self._sub = sub                    # ніколи не None
    # ...методи — на кроці 5

# єдине місце, де вирішуємо: підставити FREE замість None
def account_for(name: str, sub: Optional[Subscription]) -> Account:
    return Account(name, sub or FREE)
