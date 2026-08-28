class Db:
    """Фейкове сховище: дві «таблиці» в пам'яті; кожен похід рахуємо."""
    def __init__(self) -> None:
        self.customers = {
            1: {"id": 1, "name": "Ада",   "city": "Лондон"},
            2: {"id": 2, "name": "Грейс", "city": "Нью-Йорк"},
            3: {"id": 3, "name": "Лінус", "city": "Гельсінкі"},
        }
        # 100 замовлень, розкидані лише на трьох покупців: (i % 3) + 1
        self.orders = {
            i: {"id": i, "customer_id": (i % 3) + 1, "total": 10 * i}
            for i in range(1, 101)
        }
        self.queries = 0                                  # лічильник запитів

    def find_all_orders(self) -> list[dict]:
        self.queries += 1                                 # один SELECT на весь список
        return [dict(r) for r in self.orders.values()]

    def find_customer(self, cid: int) -> dict:
        self.queries += 1                                 # один SELECT на один рядок
        return dict(self.customers[cid])

    def find_customers(self, ids: list[int]) -> dict[int, dict]:
        self.queries += 1                                 # один SELECT ... WHERE id IN (...)
        want = set(ids)
        return {cid: dict(r) for cid, r in self.customers.items() if cid in want}

    def find_orders_join_customer(self) -> list[dict]:
        self.queries += 1                                 # один SELECT ... JOIN — покупець їде в кожному рядку
        out = []
        for r in self.orders.values():
            row = dict(r)
            row["customer"] = dict(self.customers[r["customer_id"]])
            out.append(row)
        return out
