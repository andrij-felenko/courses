class IdentityMap:
    def __init__(self, db):
        self._objects = {}                    # (тип, ключ) → об'єкт
        self._db = db

    def get(self, cls, pk):
        return self._objects.get((cls, pk))

    def add(self, obj):
        key = (type(obj), obj.pk)
        existing = self._objects.get(key)
        if existing is not None and existing is not obj:
            raise ValueError(f"{key} уже в мапі — це двійник")
        self._objects[key] = obj
        return obj

    def load(self, cls, pk):
        found = self.get(cls, pk)
        if found is not None:
            return found                      # влучання: до бази не йдемо
        row = self._db.select_one(cls.table, pk)
        return self.add(cls.from_row(row)) if row else None
