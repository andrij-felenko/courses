class Session:
    def __init__(self, db, map_factory=IdentityMap):
        self._db = db
        self.identity_map = map_factory()
        self._uow = UnitOfWork()
        self._closed = False

    def load(self, cls, pk):
        self._check_open()
        found = self.identity_map.get(cls, pk)
        if found is not None:
            return found                      # влучання: ні SELECT, ні нового об'єкта
        row = self._db.select_one(cls.table, pk)
        return self._attach(cls.from_row(row)) if row is not None else None

    def add(self, obj):
        self._check_open()
        self._attach(obj)
        self._uow.register_new(obj)
        return obj

    def delete(self, obj):
        self._check_open()
        self._uow.register_removed(obj)

    def _attach(self, obj):
        self.identity_map.add(obj)
        obj._session = self                   # відтепер його присвоєння видно
        return obj

    def _mark_dirty(self, obj, field):
        if not self._closed:
            self._uow.register_dirty(obj, field)

    def commit(self):
        self._check_open()
        self._uow.commit(self._db)
        self._db.conn.commit()

    def rollback(self):
        self._uow.forget()
        self._db.conn.rollback()
        self.identity_map.clear()             # відкат — стан у пам'яті вже несправжній

    def close(self):
        if self._closed:
            return
        if not self._uow.is_empty():
            # мовчки загубити зміни — це рівно та хвороба, яку ми лікуємо
            raise RuntimeError("сесію закривають із незаписаними змінами")
        for obj in self.identity_map.values():
            obj._session = None               # відчепити тих, хто ще живий
        self.identity_map.clear()
        self._closed = True

    def _check_open(self):
        if self._closed:
            raise RuntimeError("сесія закрита")

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        if exc_type is None:
            self.commit()
        else:
            self.rollback()
        self.close()
        return False
