// Один тик детектора. Викликати періодично (напр. раз на 100 мс) зі свіжими
// температурами зон (десяті °C) і кроком dt_ms між викликами.
// Повертає true, щойно подія поширення ПІДТВЕРДЖЕНА (і далі лишається true — засув).
bool prop_detector_tick(prop_detector_t *d, const int32_t *t_c10, uint32_t dt_ms) {
    if (d->state == PROP_LATCHED) return true;      // зафіксувалися — назад не вертаємось

    int32_t med = zones_median(t_c10, N_ZONES);
    bool suspect = false;
    int8_t who = -1;

    for (int z = 0; z < N_ZONES; z++) {
        // ознака 1: рівень — зона явно в утечі
        bool hot = (t_c10[z] >= LVL_TRIP_C10);

        // ознака 2: швидкість — крутий dT/dt саме цієї зони
        bool fast = false;
        if (d->have_prev && dt_ms > 0) {
            int32_t rate = (t_c10[z] - d->prev_c10[z]) * 1000 / (int32_t)dt_ms;
            fast = (rate >= RATE_TRIP);
        }

        // ознака 3: розкид — зона набагато гарячіша за фон пакета
        bool stands_out = ((t_c10[z] - med) >= SPREAD_TRIP);

        // подія поширення = ЗБІГ усіх трьох ознак на одній зоні
        if (hot && fast && stands_out) { suspect = true; who = (int8_t)z; break; }
    }

    // зберегти заміри для наступного dT/dt
    for (int z = 0; z < N_ZONES; z++) d->prev_c10[z] = t_c10[z];
    d->have_prev = true;

    // підтвердження персистентністю: підозра має протриматись PERSIST_TICKS поспіль
    if (suspect) {
        d->hot_zone = who;
        if (d->suspect_cnt < 255) d->suspect_cnt++;
        d->state = PROP_SUSPECT;
        if (d->suspect_cnt >= PERSIST_TICKS) {
            d->state = PROP_LATCHED;            // ПІДТВЕРДЖЕНО — фіксуємось
            return true;
        }
    } else {
        d->suspect_cnt = 0;                      // підозра зникла — скидаємо лічильник
        if (d->state == PROP_SUSPECT) d->state = PROP_IDLE;
    }
    return false;
}
