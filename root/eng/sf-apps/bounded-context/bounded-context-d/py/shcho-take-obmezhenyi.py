# Один Product на всю систему — приречений мішок суперечностей
class Product:
    def __init__(self) -> None:
        # поля каталогу
        self.title: str = ""
        self.description: str | None = None   # складу й доставці — None
        self.photos: list[str] = []           # складу й доставці — порожньо
        self.reviews: list[Review] = []       # тут узагалі чуже
        # поля складу
        self.weight_kg: float | None = None   # каталогу — None, поки не зважили
        self.shelf: str | None = None
        self.stock: int | None = None
        # поля доставки
        self.fragile: bool | None = None
        self.can_lay_flat: bool | None = None
        # ...і так до сімдесяти полів, половина вічно порожня

    def can_publish(self) -> bool:            # правило каталогу
        return self.description is not None and len(self.photos) > 0

    def can_store(self) -> bool:              # правило складу
        return self.weight_kg is not None     # нічого не знає про каталог
    # щойно створений товар: can_publish() = False, can_store() = False.
    # Він валідний чи ні? Клас не знає — бо намагається служити всім.
