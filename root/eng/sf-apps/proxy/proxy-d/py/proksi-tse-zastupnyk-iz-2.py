class ImageProxy:
    def __init__(self, path: str) -> None:
        self.path = path                # конструктор дешевий: лише запам'ятали шлях
        self._real: RealImage | None = None   # ще немає — файл не читаний

    def _load(self) -> RealImage:
        if self._real is None:
            self._real = RealImage(self.path)   # читаємо ОДИН раз
        return self._real

    def draw(self) -> None:
        self._load().draw()             # прийшли малювати → тепер треба справжній

    def width(self) -> int:
        return self._load().width()

# Клієнт не бачить різниці — тип той самий:
gallery: list[Image] = [ImageProxy(p) for p in paths]   # 2000 картинок, 0 читань із диска
gallery[0].draw()   # читається РІВНО одна — перша
