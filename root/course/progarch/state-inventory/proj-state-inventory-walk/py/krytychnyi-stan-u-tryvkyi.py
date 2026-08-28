MAX_RUN_S = 2 * 3600

def set_heating_since(ts):                       # тривкий запис — переживе рестарт
    db.execute("INSERT OR REPLACE INTO kv(k, v) VALUES ('heated_since', ?)", (ts,))
    db.commit()

def heating_since():
    row = db.execute("SELECT v FROM kv WHERE k = 'heated_since'").fetchone()
    return row[0] if row else None

def guard():                                     # межа рахує від ДИСКА, не від памʼяті
    since = heating_since()
    if relay_is_on() and since and now() - since > MAX_RUN_S:
        relay_off(); set_heating_since(None)
