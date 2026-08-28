class UnitOfWork:
    """Три списки. Сильні посилання в них — навмисне: брудний об'єкт
    не має права померти, доки його не записано."""

    def __init__(self):
        self._new = {}          # (клас, pk) → об'єкт
        self._dirty = {}        # (клас, pk) → об'єкт
        self._removed = {}      # (клас, pk) → об'єкт
        self._fields = {}       # (клас, pk) → множина змінених стовпців

    def register_new(self, obj):
        self._new[(type(obj), obj.pk)] = obj

    def register_dirty(self, obj, field):
        key = (type(obj), obj.pk)
        if key in self._new or key in self._removed:
            return              # новий і так запишеться цілком; вилучений — зникне
        self._dirty[key] = obj
        self._fields.setdefault(key, set()).add(field)

    def register_removed(self, obj):
        key = (type(obj), obj.pk)
        self._new.pop(key, None)
        self._dirty.pop(key, None)
        self._fields.pop(key, None)
        self._removed[key] = obj

    def is_empty(self):
        return not (self._new or self._dirty or self._removed)

    def forget(self):
        self._new.clear()
        self._dirty.clear()
        self._removed.clear()
        self._fields.clear()

    def commit(self, db):
        for (cls, pk), obj in self._new.items():
            db.insert(cls.table, pk, {c: getattr(obj, c) for c in cls.columns})
        for key, obj in self._dirty.items():
            cls, pk = key
            # пишемо ЛИШЕ те, що справді змінили, а не всі стовпці підряд
            db.update(cls.table, pk,
                      {c: getattr(obj, c) for c in sorted(self._fields[key])})
        for (cls, pk), obj in self._removed.items():
            db.delete(cls.table, pk)
        self.forget()           # записано — відпускаємо: об'єкти знову слабкі
