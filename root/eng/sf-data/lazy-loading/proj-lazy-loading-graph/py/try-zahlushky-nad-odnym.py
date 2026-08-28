# 1) Ліниве поле: лінь живе в самому Order — порожній слот плюс властивість.
class OrderLazyField:
    def __init__(self, db: Db, row: dict) -> None:
        self._db = db
        self.id = row["id"]
        self.total = row["total"]
        self._customer_id = row["customer_id"]
        self._customer: dict | None = None                # ще не тягли
    @property
    def customer(self) -> dict:
        if self._customer is None:
            self._customer = self._db.find_customer(self._customer_id)
        return self._customer

# 2) Віртуальний проксі: ОКРЕМИЙ об'єкт із тим самим інтерфейсом, що й покупець.
class CustomerProxy:
    def __init__(self, db: Db, cid: int) -> None:
        self._db, self._cid, self._real = db, cid, None
    def _load(self) -> dict:
        if self._real is None:
            self._real = self._db.find_customer(self._cid)  # справжнього створює раз
        return self._real
    @property
    def name(self) -> str: return self._load()["name"]      # кожен метод делегує
    @property
    def city(self) -> str: return self._load()["city"]

# 3) Привид: сам покупець, але створений з одним id і порожніми полями.
class CustomerGhost:
    def __init__(self, db: Db, cid: int) -> None:
        self._db = db
        self.id = cid                                       # тотожність правильна від початку
        self._loaded = False
        self._name = self._city = ""
    def _fill(self) -> None:
        if not self._loaded:
            row = self._db.find_customer(self.id)           # один запит — і ВСІ поля разом
            self._name, self._city = row["name"], row["city"]
            self._loaded = True
    @property
    def name(self) -> str: self._fill(); return self._name
    @property
    def city(self) -> str: self._fill(); return self._city
