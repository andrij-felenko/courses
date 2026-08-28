def reconcile(conn) -> tuple[int, int]:
    """Гейт: (скільки ще NULL, скільки розбіжностей). Пускаємо далі лише коли ОБИДВА = 0."""
    nulls = mismatches = 0
    last_id = 0
    with conn.cursor() as cur:
        while True:
            cur.execute(
                "SELECT id, temp_c, temp_mc FROM readings "
                "WHERE id > %s ORDER BY id LIMIT %s",
                (last_id, 50_000),
            )
            rows = cur.fetchall()
            if not rows:
                break
            for rid, temp_c, temp_mc in rows:
                if temp_mc is None:
                    nulls += 1
                elif temp_mc != to_milli_c(temp_c):      # ТОЙ САМИЙ перетвір, що в записі
                    mismatches += 1
            last_id = rows[-1][0]
    return nulls, mismatches
