# Одна формула переливу — ОДНЕ місце на весь проєкт.
# Її вживають і подвійний запис, і бекфіл, і звірка — інакше вони розійдуться.
def to_milli_c(temp_c: float) -> int:
    return round(temp_c * 1000)                 # 23.5 °C → 23500

def insert_reading(cur, device_id: int, ts, temp_c: float) -> None:
    # Пишемо в ОБИДВІ колонки в ОДНОМУ INSERT — один рядок, одна транзакція:
    # старе й нове не можуть розійтися, бо кладуться разом або ніяк.
    cur.execute(
        "INSERT INTO readings (device_id, ts, temp_c, temp_mc) "
        "VALUES (%s, %s, %s, %s)",
        (device_id, ts, temp_c, to_milli_c(temp_c)),
    )
