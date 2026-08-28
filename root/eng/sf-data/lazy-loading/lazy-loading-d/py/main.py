class Order:
    def __init__(self, id: int, customer_id: int) -> None:
        self.id = id
        self._customer_id = customer_id
        self._customer: Customer | None = None          # ще не тягнули

    @property
    def customer(self) -> Customer:
        if self._customer is None:
            self._customer = db.load_customer(self._customer_id)   # один похід у базу
        return self._customer
