def save_home(reg: sqlite3.Connection, home: dict) -> None:
    reg.execute("BEGIN")                              # відкриваємо межу агрегату
    try:
        reg.execute(
            "INSERT INTO homes(id, owner, threshold, heat_left) "
            "VALUES(:id, :owner, :threshold, :heat_left) "
            "ON CONFLICT(id) DO UPDATE SET "           # поклади АБО онови — але heat_left НЕ чіпаємо:
            "  owner=excluded.owner, threshold=excluded.threshold",   # бюджет живе своїм життям
            home)
        reg.execute("DELETE FROM devices WHERE home_id = ?", (home["id"],))
        reg.executemany(
            "INSERT INTO devices(home_id, id, kind, room) VALUES(?,?,?,?)",
            [(home["id"], d["id"], d["kind"], d["room"]) for d in home["devices"]])
        reg.execute("COMMIT")                          # ОДНА мить, у яку весь дім стає видимим
    except Exception:
        reg.execute("ROLLBACK")
        raise
