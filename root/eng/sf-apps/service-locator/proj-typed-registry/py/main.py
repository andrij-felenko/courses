from typing import TypeVar, Protocol, cast

T = TypeVar("T")

class PaymentGateway(Protocol):
    def charge(self, amount: int) -> None: ...

class ServiceRegistry:
    def __init__(self) -> None:
        self._map: dict[type, object] = {}

    def register(self, key: type[T], value: T) -> None:
        self._map[key] = value

    def resolve(self, key: type[T]) -> T:
        if key not in self._map:
            raise LookupError(f"Служба не зареєстрована: {key.__name__}")
        return cast(T, self._map[key])   # єдине приведення, як і в TS

registry.register(PaymentGateway, StripeGateway())  # клас — це ключ
gateway = registry.resolve(PaymentGateway)          # mypy бачить тип PaymentGateway
# registry.resolve(PymentGateway)                   # ✗ NameError на самій згадці
