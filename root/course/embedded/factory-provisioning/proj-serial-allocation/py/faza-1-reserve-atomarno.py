import sqlite3, time

def reserve(db_path: str, station: str) -> int:
    """Фаза 1: атомарно зарезервувати найменший вільний номер за станцією.
       Повертає зарезервований серійник. Кидає, якщо вільних немає."""
    conn = sqlite3.connect(db_path, isolation_level=None)  # керуємо транзакцією самі
    try:
        # BEGIN IMMEDIATE бере замок на запис ОДРАЗУ, на початку транзакції.
        # Друга голова, що теж робить reserve, чекатиме тут, а не влізе всередину.
        conn.execute("BEGIN IMMEDIATE")

        # Атомарно: перевести найменший 'free' у 'reserved' і ПОВЕРНУТИ його номер.
        # UPDATE ... RETURNING робить пошук+зміну+повернення однією операцією —
        # немає вікна між 'прочитав вільний' і 'зайняв його', у яке влізла б інша голова.
        row = conn.execute("""
            UPDATE serials
               SET state = 'reserved', station = ?, reserved_at = ?
             WHERE serial = (SELECT MIN(serial) FROM serials WHERE state = 'free')
         RETURNING serial
        """, (station, int(time.time()))).fetchone()

        if row is None:
            conn.execute("ROLLBACK")
            raise RuntimeError("серійники скінчилися: немає жодного вільного")

        conn.execute("COMMIT")   # тільки ТУТ резерв стає видимим іншим головам
        return row[0]
    except Exception:
        conn.execute("ROLLBACK")
        raise
    finally:
        conn.close()
