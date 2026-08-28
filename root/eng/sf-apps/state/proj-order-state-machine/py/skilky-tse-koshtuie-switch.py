# Уся таблиця як дані: (стан, подія) → наступний стан або спеціальна мітка.
TABLE = {
    "New":       {"pay": "Paid", "cancel": "Cancelled",
                  "ship": "reject", "refund": "reject"},
    "Paid":      {"ship": "Shipped", "cancel": "Refunded", "refund": "Refunded",
                  "pay": "reject"},
    "Shipped":   {"refund": "Refunded", "ship": "ignore",
                  "pay": "reject", "cancel": "reject"},
    "Cancelled": {"cancel": "ignore", "pay": "reject",
                  "ship": "reject", "refund": "reject"},
    "Refunded":  {"refund": "ignore", "pay": "reject",
                  "ship": "reject", "cancel": "reject"},
}


class Order:
    def __init__(self, id: str) -> None:
        self.id = id
        self.state = "New"
        self.logbook: list[str] = []

    def fire(self, event: str) -> None:         # ОДИН рушій на всі події
        cell = TABLE.get(self.state, {}).get(event)
        if cell is None or cell == "reject":
            raise Exception(f"не можна {event}: стан «{self.state}»")
        if cell == "ignore":
            self.logbook.append(f"ігнор: {event}")
            return
        self.logbook.append(f"{self.state} → {cell}")
        self.state = cell                        # + тут же побічна дія події, якщо треба

    def pay(self):    self.fire("pay")
    def ship(self):   self.fire("ship")
    def cancel(self): self.fire("cancel")
    def refund(self): self.fire("refund")
