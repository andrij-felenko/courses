from dataclasses import dataclass
from typing import Dict, List, Set, Optional

@dataclass
class OrderRecord:
    id: str
    status: str
    amount_cents: int

@dataclass
class LedgerLine:
    account_id: str
    debit_cents: int
    credit_cents: int

class OrderFulfillmentCoordinator:
    def __init__(self):
        self._processed_events: Set[str] = set()
        self._orders: Dict[str, OrderRecord] = {
            "ord_884920": OrderRecord(id="ord_884920", status="PENDING", amount_cents=10990)
        }
        self._ledger: List[LedgerLine] = []

    def handle_payment_succeeded(self, event: Dict) -> str:
        event_id = event["id"]

        # 1. Дедуплікація
        if event_id in self._processed_events:
            return "ALREADY_PROCESSED"

        obj = event["data"]["object"]
        order_id = obj.get("metadata", {}).get("order_id")
        order = self._orders.get(order_id)

        if not order:
            raise KeyError(f"Замовлення {order_id} не знайдено")

        # 2. Монотонний State Guard
        if order.status == "PAID":
            self._processed_events.add(event_id)
            return "IGNORED_OLD_STATE"

        # 3. Оновлення стану та запис до Ledger
        order.status = "PAID"
        amount = obj["amount"]
        fee = round(amount * 0.029 + 30)

        # Проводки подвійного запису
        self._ledger.extend([
            LedgerLine(account_id="1010-PSP-CLEARING", debit_cents=amount, credit_cents=0),
            LedgerLine(account_id="4010-SALES-REVENUE", debit_cents=0, credit_cents=amount),
            LedgerLine(account_id="5010-GATEWAY-EXPENSE", debit_cents=fee, credit_cents=0),
            LedgerLine(account_id="1010-PSP-CLEARING", debit_cents=0, credit_cents=fee),
        ])

        self._processed_events.add(event_id)
        return "PROCESSED"
