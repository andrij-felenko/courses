import weakref


class IdentityMap:
    """(клас, pk) → об'єкт. Значення слабкі: мапа нікого не тримає живим."""

    def _new_bucket(self):
        return weakref.WeakValueDictionary()

    def __init__(self):
        self._by_type = {}

    def get(self, cls, pk):
        bucket = self._by_type.get(cls)
        return bucket.get(pk) if bucket is not None else None

    def add(self, obj):
        bucket = self._by_type.setdefault(type(obj), self._new_bucket())
        existing = bucket.get(obj.pk)
        if existing is not None and existing is not obj:
            raise ValueError(f"({type(obj).__name__}, {obj.pk}) уже в мапі — це двійник")
        bucket[obj.pk] = obj
        return obj

    def values(self):
        return [o for b in self._by_type.values() for o in list(b.values())]

    def clear(self):
        self._by_type.clear()

    def __len__(self):
        return sum(len(b) for b in self._by_type.values())
