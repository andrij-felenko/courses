_MISSING = object()


class Entity:
    """Сутність: тотожність — це (клас, pk); значення полів до неї не належать."""

    table = ""
    columns = ()

    def __init__(self, pk, **values):
        self._session = None            # хто веде цей об'єкт; None — відчеплений
        self.pk = pk
        for name in self.columns:
            setattr(self, name, values[name])

    def __setattr__(self, name, value):
        old = getattr(self, name, _MISSING)
        object.__setattr__(self, name, value)
        # _MISSING — це перше присвоєння, тобто складання об'єкта з рядка:
        # воно бруду не робить. Далі — лише СПРАВЖНЯ зміна СПРАВЖНЬОГО стовпця.
        if old is not _MISSING and old != value and name in self.columns:
            session = self._session
            if session is not None:
                session._mark_dirty(self, name)

    @classmethod
    def from_row(cls, row):
        return cls(row["id"], **{c: row[c] for c in cls.columns})


class Order(Entity):
    table = "orders"
    columns = ("status", "discount")
