# Один тик детектора. Викликати періодично (напр. раз на 100 мс) зі свіжими
# температурами зон (десяті °C) і кроком dt_ms між викликами.
# Повертає True, щойно подія поширення ПІДТВЕРДЖЕНА (і далі лишається True — засув).
def prop_detector_tick(d: PropDetector, t_c10, dt_ms: int) -> bool:
    if d.state == PropState.LATCHED:
        return True                              # зафіксувалися — назад не вертаємось

    med = zones_median(t_c10, N_ZONES)
    suspect = False
    who = -1

    for z in range(N_ZONES):
        # ознака 1: рівень — зона явно в утечі
        hot = t_c10[z] >= LVL_TRIP_C10

        # ознака 2: швидкість — крутий dT/dt саме цієї зони
        fast = False
        if d.have_prev and dt_ms > 0:
            rate = (t_c10[z] - d.prev_c10[z]) * 1000 // dt_ms
            fast = rate >= RATE_TRIP

        # ознака 3: розкид — зона набагато гарячіша за фон пакета
        stands_out = (t_c10[z] - med) >= SPREAD_TRIP

        # подія поширення = ЗБІГ усіх трьох ознак на одній зоні
        if hot and fast and stands_out:
            suspect = True
            who = z
            break

    # зберегти заміри для наступного dT/dt
    d.prev_c10 = list(t_c10[:N_ZONES])
    d.have_prev = True

    # підтвердження персистентністю: підозра має протриматись PERSIST_TICKS поспіль
    if suspect:
        d.hot_zone = who
        if d.suspect_cnt < 255:
            d.suspect_cnt += 1
        d.state = PropState.SUSPECT
        if d.suspect_cnt >= PERSIST_TICKS:
            d.state = PropState.LATCHED          # ПІДТВЕРДЖЕНО — фіксуємось
            return True
    else:
        d.suspect_cnt = 0                        # підозра зникла — скидаємо лічильник
        if d.state == PropState.SUSPECT:
            d.state = PropState.IDLE
    return False
