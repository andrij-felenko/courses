class Policy:
    def __init__(self, policy_id: str, currency: str, due_date):
        # поля закриті угодою про підкреслення; міняти ззовні — зась
        self._id = policy_id
        self._currency = currency
        self._due_date = due_date
        self._status = "draft"
        self._premium = 0
        self._payments = []

    # назовні — лише читання того, що справді потрібне іншим шарам
    @property
    def id(self) -> str:
        return self._id

    @property
    def status(self) -> str:
        return self._status

    @property
    def premium(self) -> int:
        return self._premium
    # ЖОДНОГО сеттера на status / premium: змінити стан ззовні вже не можна
