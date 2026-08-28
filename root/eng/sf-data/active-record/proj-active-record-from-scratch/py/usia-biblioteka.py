import sqlite3

_UNSET = object()


class StaleObject(Exception):
    """Рядок змінив хтось інший, поки ми тримали цей об'єкт."""


class Record:
    table = ""            # ім'я таблиці
    pk = "id"             # первинний ключ
    version = None        # колонка-лічильник або None
    db = None             # sqlite3.Connection

    # ── схема: клас питає базу, які в нього поля ──
    @classmethod
    def columns(cls):
        if "_columns" not in cls.__dict__:          # кеш саме цього класу
            info = cls.db.execute(f'PRAGMA table_info("{cls.table}")').fetchall()
            if not info:
                raise LookupError(f'таблиці "{cls.table}" немає')
            cls._columns = tuple(row[1] for row in info)
        return cls._columns

    # ── брудний набір: перехоплюємо присвоєння ──
    def __init__(self, **fields):
        object.__setattr__(self, "_data", {c: None for c in type(self).columns()})
        object.__setattr__(self, "_dirty", set())
        for name, value in fields.items():
            setattr(self, name, value)

    def __setattr__(self, name, value):
        if name not in type(self).columns():        # не колонка — звичайний атрибут
            object.__setattr__(self, name, value)
            return
        if self._data.get(name, _UNSET) != value:   # те саме значення не бруднить
            self._dirty.add(name)
        self._data[name] = value

    def __getattr__(self, name):                    # лише коли не знайшли інакше
        try:
            return self.__dict__["_data"][name]
        except KeyError:
            raise AttributeError(name) from None

    def changes(self):
        return {c: self._data[c] for c in sorted(self._dirty)}

    # ── читання ──
    @classmethod
    def _from_row(cls, row):
        obj = cls.__new__(cls)                      # __init__ не потрібен: рядок готовий
        object.__setattr__(obj, "_data", dict(zip(cls.columns(), row)))
        object.__setattr__(obj, "_dirty", set())    # щойно з бази → чистий
        return obj

    @classmethod
    def find(cls, key):
        names = ", ".join(f'"{c}"' for c in cls.columns())
        row = cls.db.execute(
            f'SELECT {names} FROM "{cls.table}" WHERE "{cls.pk}" = ?', (key,)
        ).fetchone()
        return cls._from_row(row) if row else None

    @classmethod
    def where(cls, **cond):
        for c in cond:
            if c not in cls.columns():              # у SQL іде лише те, що дала схема
                raise LookupError(f'колонки "{c}" в "{cls.table}" немає')
        names = ", ".join(f'"{c}"' for c in cls.columns())
        sql = f'SELECT {names} FROM "{cls.table}"'
        if cond:
            sql += " WHERE " + " AND ".join(f'"{c}" = ?' for c in cond)
        return [cls._from_row(r) for r in cls.db.execute(sql, tuple(cond.values()))]

    # ── запис ──
    def save(self):
        return self._insert() if self._data[type(self).pk] is None else self._update()

    def _insert(self):
        cls = type(self)
        if cls.version:
            self._data[cls.version] = 0
            self._dirty.add(cls.version)
        cols = [c for c in cls.columns() if c in self._dirty]
        if cols:
            names = ", ".join(f'"{c}"' for c in cols)
            marks = ", ".join("?" for _ in cols)
            cur = cls.db.execute(f'INSERT INTO "{cls.table}" ({names}) VALUES ({marks})',
                                 [self._data[c] for c in cols])
        else:
            cur = cls.db.execute(f'INSERT INTO "{cls.table}" DEFAULT VALUES')
        self._data[cls.pk] = cur.lastrowid
        self._dirty.clear()
        return 1

    def _update(self):
        cls = type(self)
        cols = [c for c in cls.columns()
                if c in self._dirty and c != cls.pk and c != cls.version]
        if not cols:
            return 0                                # нічого не змінилося — жодного запиту
        sets = [f'"{c}" = ?' for c in cols]
        args = [self._data[c] for c in cols]
        where, wargs = f'"{cls.pk}" = ?', [self._data[cls.pk]]
        if cls.version:
            seen = self._data[cls.version] or 0
            sets.append(f'"{cls.version}" = ?')
            args.append(seen + 1)
            where += f' AND "{cls.version}" = ?'    # рядок мусить бути тим, що ми читали
            wargs.append(seen)
        cur = cls.db.execute(
            f'UPDATE "{cls.table}" SET {", ".join(sets)} WHERE {where}', args + wargs)
        if cur.rowcount != 1:                       # 0 рядків → версія вже не наша
            raise StaleObject(f'{cls.__name__} {self._data[cls.pk]}: рядок змінили')
        if cls.version:
            self._data[cls.version] = seen + 1
        self._dirty.clear()
        return 1

    def delete(self):
        cls = type(self)
        key = self._data[cls.pk]
        if key is None:
            return 0
        cur = cls.db.execute(f'DELETE FROM "{cls.table}" WHERE "{cls.pk}" = ?', (key,))
        self._data[cls.pk] = None                   # ключа немає → рядка немає
        object.__setattr__(self, "_dirty", {c for c in cls.columns()
                                            if c != cls.pk and self._data[c] is not None})
        return cur.rowcount
