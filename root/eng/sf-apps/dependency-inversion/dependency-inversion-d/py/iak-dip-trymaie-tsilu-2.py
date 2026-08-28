from domain import Orders, Order, OrderId        # деталь залежить УГОРУ, від домену

class PgOrders:                                  # структурно задовольняє Orders (Protocol)
    def __init__(self, db):
        self._db = db

    async def save(self, o: Order) -> None:
        await self._db.exec("insert into orders ...", o.row())

    async def by_id(self, id: OrderId):
        r = await self._db.query("select ... where id = $1", id.value)
        return Order.from_row(r[0]) if r else None
