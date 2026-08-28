# НЕ так: сервіс сам лізе по глобальний конфіг
class OrderService:
    def place_order(self, order):
        cfg = Config.get_instance()            # прихована залежність
        ...

# А так: залежність приходить явно через конструктор
class OrderService:
    def __init__(self, cfg: Config):           # видно в сигнатурі
        self._cfg = cfg
    def place_order(self, order):
        ...                                    # користуємось self._cfg
