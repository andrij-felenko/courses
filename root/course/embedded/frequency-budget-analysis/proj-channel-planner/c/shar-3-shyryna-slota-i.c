void plan_channels(const radio_spec *r, channel_plan *out) {
    // 1. Дрейф несної з одного боку (кварц + Доплер).
    out->drift_one_hz = carrier_drift_one_side(r);

    // 2. Ширина слота: W = B + 2·Δf + G.
    //    Множник 2 — бо несна їде в ОБИДВА боки (тx +Δf, rx −Δf).
    out->slot_hz = r->signal_bw_hz
                 + 2.0 * out->drift_one_hz       // ← НЕ забути 2.0!
                 + r->guard_hz;

    // 3. Скільки цілих слотів влазить у смугу — округлення ВНИЗ.
    //    floor, бо半-канал не існує: 41.7 слота = 41 канал, не 42.
    out->channels = (int) floor(r->band_hz / out->slot_hz);
    if (out->channels < 0) out->channels = 0;    // захист від дурних вхідних

    // 4. Частка слота, що пішла НЕ на корисний сигнал (накладні).
    out->overhead_frac = (out->slot_hz - r->signal_bw_hz) / out->slot_hz;
}
