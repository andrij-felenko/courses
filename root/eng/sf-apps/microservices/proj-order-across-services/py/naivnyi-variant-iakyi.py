# НАЇВНО — не робіть так. Два віддалені записи без спільної транзакції.
class OrderService:
    def __init__(self, orders: OrderRepository, stock: StockClient) -> None:
        self._orders = orders   # приватна база замовлень
        self._stock = stock     # HTTP-клієнт до сервісу складу

    async def place_order(self, cmd: PlaceOrder) -> str:
        order = Order.create(cmd.customer_id, cmd.items)

        # КРОК 1: віддалений виклик — склад списує товар у СВОЇЙ базі
        await self._stock.reserve(order.items)   # склад списав ✓

        # ── ⟵ якщо процес упаде рівно ТУТ, товар списаний, а рядок нижче не виконається ──

        # КРОК 2: записуємо замовлення у ВЛАСНУ базу
        await self._orders.save(order)           # а сюди вже не дійшли ✗

        return order.id
