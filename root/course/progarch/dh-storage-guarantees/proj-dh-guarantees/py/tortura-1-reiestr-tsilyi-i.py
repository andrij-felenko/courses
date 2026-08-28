def _writer_home_before_commit(path, home, brink):
    reg = open_registry(path)
    reg.execute("BEGIN")
    reg.execute("INSERT INTO homes(id, owner, threshold, heat_left) "
                "VALUES(:id,:owner,:threshold,:heat_left) "
                "ON CONFLICT(id) DO UPDATE SET threshold=excluded.threshold", home)
    reg.execute("DELETE FROM devices WHERE home_id=?", (home["id"],))
    reg.executemany("INSERT INTO devices(home_id,id,kind,room) VALUES(?,?,?,?)",
                    [(home["id"], d["id"], d["kind"], d["room"]) for d in home["devices"]])
    brink.set()                 # усе зроблено, COMMIT ще НЕ викликано — межа небезпеки
    import time; time.sleep(3600)   # паркуємось тут, доки батько не вбʼє
    reg.execute("COMMIT")           # сюди виконання не дійде
