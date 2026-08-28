RangeResult rf_update(RangeFilter *f, Sample s) {
    RangeResult r; r.conf = 0.0f;

    /* 0. Пропуск (dropout): нема відлуння або сигнал нижче підлоги довіри. */
    if (!s.valid || s.strength < f->floor) {
        f->drops++;
        if (f->have_est && f->drops <= f->max_drops) {   // коротка сліпота —
            r.status = RF_HELD;                          // тримаємо останнє відоме
            r.mm = r.med_mm = (uint16_t)(f->est + 0.5f);
            return r;
        }
        f->have_last = false;          // довга сліпота — рвемо опору воріт
        r.status = RF_LOST;            // і чесно кажемо «не знаю»
        r.mm = r.med_mm = 0;
        return r;                      // для уникання зіткнень це НЕБЕЗПЕКА, не «вільно»
    }
    f->drops = 0;

    /* 1. Медіана-3 у кільцевому буфері — вбити поодинокий викид. */
    f->ring[f->head] = s.dist_mm;
    f->head = (uint8_t)((f->head + 1) % 3);
    if (f->fill < 3) f->fill++;
    uint16_t med = (f->fill == 3)
                 ? median3(f->ring[0], f->ring[1], f->ring[2])
                 : s.dist_mm;          // поки буфер не повний — беремо як є

    /* 2. Ворота швидкості: за Δt ціль не могла зрушити більш ніж на v_макс·Δt. */
    if (f->have_last) {
        uint32_t dt   = s.t_ms - f->last_ms;                    // різниця uint32 коректна й на перевороті лічильника мс
        uint32_t dmax = (uint32_t)f->vmax_mm_s * dt / 1000u + f->margin_mm;
        uint16_t jump = (med > f->last_mm) ? (uint16_t)(med - f->last_mm)
                                           : (uint16_t)(f->last_mm - med);
        if (jump > dmax) {
            f->rejects++;
            if (f->rejects <= f->max_rejects) {   // фізично неможливий стрибок — викид
                r.status = RF_HELD;
                r.mm = r.med_mm = (uint16_t)(f->est + 0.5f);
                return r;
            }
            f->est = med;   // стільки «неможливих» поспіль — це вже реальна зміна світу
        }                   // (або ми застрягли на привиді): пере-захоплюємо
    }
    f->rejects = 0;

    /* 3. Довіра за силою відлуння → вага [0..1]. */
    float conf = confidence(s.strength, f->floor, f->full);

    /* 4. Зважене злиття: крок до медіани пропорційний довірі. */
    if (!f->have_est) { f->est = med; f->have_est = true; }
    else {
        float alpha = f->base_alpha * conf;     // кволий сигнал → майже не рухаємо оцінку
        f->est += alpha * ((float)med - f->est);
    }

    f->last_mm = med; f->last_ms = s.t_ms; f->have_last = true;

    r.status = RF_FRESH;
    r.conf   = conf;
    r.med_mm = med;                          // крайо-зберігаючий вихід — для безпеки
    r.mm     = (uint16_t)(f->est + 0.5f);    // згладжений за довірою — для показу
    return r;
}

void rf_init(RangeFilter *f, uint16_t vmax_mm_s, uint16_t floor, uint16_t full) {
    memset(f, 0, sizeof(*f));
    f->vmax_mm_s = vmax_mm_s;   // найгірша швидкість ЗБЛИЖЕННЯ, не лише ваша
    f->floor = floor;           // нижче — dropout
    f->full  = full;            // вище — повна довіра
    f->margin_mm  = 15;         // запас на шум самого виміру
    f->base_alpha = 0.6f;       // жвавість злиття при повній довірі
    f->max_drops   = 3;         // 3 пропуски тримаємо старе, тоді LOST
    f->max_rejects = 4;         // 4 «неможливих» поспіль → пере-захоплення
}
