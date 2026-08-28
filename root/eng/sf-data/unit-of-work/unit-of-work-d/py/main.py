class UnitOfWork:
    def __init__(self, conn, mappers):
        self._conn = conn                 # одне з'єднання = одна транзакція
        self._mappers = mappers           # тип сутності → її Data Mapper
        self._new, self._dirty, self._removed = [], [], []

    def register_new(self, obj):
        self._new.append(obj)             # цього ще немає в базі — вставити

    def register_dirty(self, obj):        # цей у базі є й змінився — оновити
        if obj not in self._dirty and obj not in self._new:
            self._dirty.append(obj)

    def register_removed(self, obj):      # цей у базі є й має зникнути — видалити
        if obj in self._new:
            self._new.remove(obj)         # народжене й одразу вбите — базі байдуже
            return
        if obj not in self._removed:
            self._removed.append(obj)

    def commit(self):
        try:
            for obj in self._new:      self._mappers[type(obj)].insert(obj, self._conn)
            for obj in self._dirty:    self._mappers[type(obj)].update(obj, self._conn)
            for obj in self._removed:  self._mappers[type(obj)].delete(obj, self._conn)
            self._conn.commit()           # одна транзакція на всі зміни
        except Exception:
            self._conn.rollback()         # усе або нічого
            raise
        finally:
            self._new.clear(); self._dirty.clear(); self._removed.clear()
