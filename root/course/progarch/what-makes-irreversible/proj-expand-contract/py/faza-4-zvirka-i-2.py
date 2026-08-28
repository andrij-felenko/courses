def read_temp_milli_c(cur, reading_id: int, flags) -> int:
    cur.execute("SELECT temp_c, temp_mc FROM readings WHERE id = %s", (reading_id,))
    temp_c, temp_mc = cur.fetchone()

    if flags.read_from_new:
        # Нове — джерело правди. Але поки не прибрали старе, у «тіньовому»
        # режимі звіряємо на льоту й голосно скаржимось на будь-яку розбіжність.
        if flags.shadow_compare and temp_mc != to_milli_c(temp_c):
            log.warning("divergence id=%s new=%s old=%s",
                        reading_id, temp_mc, to_milli_c(temp_c))
        return temp_mc

    # Прапорець вимкнено → читаємо СТАРЕ. Це наша дорога назад:
    # один тумблер повертає всіх читачів на перевірену колонку.
    return to_milli_c(temp_c)
