class OrderService:
    def __init__(self, logger: Logger) -> None:
        self._logger = logger        # завжди Logger, ніколи None

    def place(self, order: Order) -> None:
        # ...оформлення замовлення...
        self._logger.write(f"замовлення {order.id} оформлено")  # без перевірки

# логування ввімкнене:
OrderService(FileLogger("orders.log"))
# вимкнене — ПОРОЖНІЙ об'єкт, не None:
OrderService(NullLogger())
