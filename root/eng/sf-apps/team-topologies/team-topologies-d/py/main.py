# Командний API платформи = програмний API.
# Потокова команда бачить лише це — не знає ні черг, ні реплік, ні дата-центрів.
from typing import Callable, Protocol


class Platform(Protocol):
    # «Ми надаємо публікацію події як сервіс. Виклик синхронний, доставка гарантована.»
    def publish(self, topic: str, payload: str) -> bool: ...

    # «Підписка — теж наш сервіс. Ви даєте обробник, решта — наша справа.»
    def subscribe(self, topic: str, handler: Callable[[str], None]) -> None: ...
