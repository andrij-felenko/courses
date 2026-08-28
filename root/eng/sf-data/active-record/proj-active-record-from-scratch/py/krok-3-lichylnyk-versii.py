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
