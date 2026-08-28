# Python: __getattr__ спрацьовує на доступ до атрибута, якого В САМОМУ проксі немає.
# Повертаємо загорнуту функцію — одна точка на всі методи делегата.
class LoggingProxy:
    def __init__(self, real: object) -> None:
        object.__setattr__(self, "_real", real)   # обходимо власний __getattr__

    def __getattr__(self, name: str):
        attr = getattr(self._real, name)          # дістали справжній метод/поле
        if not callable(attr):
            return attr                            # поле — віддаємо як є
        def wrapper(*args, **kwargs):              # ← ЄДИНА точка для всіх методів
            log(f"→ {name}{args}")
            result = attr(*args, **kwargs)         # делегуємо справжньому
            log(f"← {name} = {result!r}")
            return result
        return wrapper

# Один проксі накриває ВЕСЬ інтерфейс, скільки б методів у ньому не було:
service: OrderService = LoggingProxy(RealOrderService())   # type: ignore[assignment]
service.get_order("ord-42")   # __getattr__("get_order") → wrapper → лог + делегування
service.place_order(order)    # той самий шлях, ані рядка окремо під нього не писали
