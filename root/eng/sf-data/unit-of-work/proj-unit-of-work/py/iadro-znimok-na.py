import copy

class UnitOfWork:
    def __init__(self, conn, mappers):
        self._conn = conn
        self._cur = conn.cursor()
        self._mappers = {m.entity: m for m in mappers}
        self._identity = {}        # (тип, ключ) → об'єкт  — карта тотожності
        self._snapshots = {}       # об'єкт → знімок полів
        self._new, self._removed = [], []

    # ── завантаження: тут народжується і карта, і знімок ──
    def read(self, cls, id):
        key = (cls, id)
        if key in self._identity:
            return self._identity[key]                 # той самий об'єкт — Identity Map
        obj = self._mappers[cls].load(id, self._cur)   # Data Mapper дістає рядок
        if obj is None:
            return None
        self._identity[key] = obj
        self._snapshot(obj)                            # запам'ятати стан на мить читання
        return obj

    def _snapshot(self, obj):
        self._snapshots[obj] = copy.deepcopy(self._mappers[type(obj)].fields(obj))

    # ── явна реєстрація для того, чого знімок не вгадає ──
    def register_new(self, obj):
        self._new.append(obj)                          # ключа ще нема — в карту потрапить на зливі
    def register_removed(self, obj):
        if obj in self._new:
            self._new.remove(obj); return              # народжене й убите — базі байдуже
        if obj not in self._removed:
            self._removed.append(obj)

    # ── автовідстеження: хто розійшовся зі своїм знімком ──
    def _dirty(self):
        out = []
        for obj, snap in self._snapshots.items():
            if obj in self._removed:
                continue
            if self._mappers[type(obj)].fields(obj) != snap:   # хоч одне поле інше
                out.append(obj)
        return out

    # ── топосорт за залежностями маперів: батько перед дитиною ──
    def _toposort(self, objs):
        order, seen = [], set()
        def visit(t):
            if t in seen: return
            seen.add(t)
            for parent in self._mappers[t].depends_on:
                visit(parent)
            order.append(t)                            # батьки лягають раніше
        for o in objs:
            visit(type(o))
        rank = {t: i for i, t in enumerate(order)}
        return sorted(objs, key=lambda o: rank[type(o)])

    # ── злив: проштовхнути SQL у транзакцію (ще НЕ завершити її) ──
    def flush(self):
        dirty = self._dirty()                          # порахувати ДО вставок
        for obj in self._toposort(self._new):          # згори вниз: батьки першими
            self._mappers[type(obj)].insert(obj, self._cur)   # призначає obj.id
            self._identity[(type(obj), obj.id)] = obj         # аж тепер має ключ → у карту
            self._snapshot(obj)                               # свіжий базовий знімок
        for obj in dirty:
            self._mappers[type(obj)].update(obj, self._cur)
            self._snapshot(obj)                               # скинути «брудність»
        for obj in reversed(self._toposort(self._removed)):   # знизу вгору: діти першими
            self._mappers[type(obj)].delete(obj, self._cur)
            self._identity.pop((type(obj), obj.id), None)
            self._snapshots.pop(obj, None)
        self._new.clear(); self._removed.clear()

    # ── фіксація: злити, а тоді завершити транзакцію ──
    def commit(self):
        try:
            self.flush()                               # увесь накопичений SQL
            self._conn.commit()                        # і аж тепер — остаточно
        except Exception:
            self._conn.rollback()                      # усе або нічого
            raise
