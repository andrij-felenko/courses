# Контекст КАТАЛОГУ: товар — це те, що показують і продають
class CatalogProduct:
    def __init__(self, title: str, description: str, photos: list[str]) -> None:
        if not photos:
            raise ValueError("товар каталогу без фото не буває")
        self.title = title
        self.description = description   # без опису товару каталогу не існує
        self.photos = photos
        # тут немає ваги й полиці — вони цьому світу не потрібні

# Контекст СКЛАДУ: товар — це фізична одиниця зберігання
class WarehouseProduct:
    def __init__(self, sku: str, weight_kg: float, shelf: str) -> None:
        self.sku = sku
        self.weight_kg = weight_kg       # без ваги на склад не приймають
        self.shelf = shelf
        # тут немає опису й відгуків — складу байдуже
