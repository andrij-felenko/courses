class AccessDenied(Exception):        # окремий тип, щоб клієнт міг його впіймати
    pass

class ProtectedOrderService:
    def __init__(self, real: OrderService, user: "User") -> None:
        self._real = real              # кого захищаємо (делегат)
        self._user = user              # від чийого імені йдуть виклики

    def _require(self, permission: str) -> None:
        if not self._user.can(permission):   # одна точка перевірки для всіх методів
            raise AccessDenied(f"{self._user.name}: немає права {permission}")

    def get_order(self, id: str) -> "Order":
        self._require("orders:read")    # спершу право...
        return self._real.get_order(id) # ...тоді делегуємо

    def place_order(self, order: "Order") -> str:
        self._require("orders:write")
        return self._real.place_order(order)

    def cancel_order(self, id: str) -> None:
        self._require("orders:cancel")
        self._real.cancel_order(id)
