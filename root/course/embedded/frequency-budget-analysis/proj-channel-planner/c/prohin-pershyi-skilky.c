int main(void) {
    // ── BLE: 2.4 ГГц, кварц ±40 ppm, GFSK на 1 Мбіт/с ────────────────────
    radio_spec ble = {
        .carrier_hz   = 2.4e9,      // несна 2.4 ГГц
        .ppm          = 40.0,       // типовий кварц ±40 ppm
        .signal_bw_hz = 1.0e6,      // смуга GFSK-сигналу BLE ≈ 1 МГц
        .guard_hz     = 0.8e6,      // захисний проміжок ≈ 0.8 МГц
        .rel_speed_ms = 0.0,        // нерухомі пристрої — Доплера нема
        .band_hz      = 83.5e6,     // уся ISM-смуга 2.400–2.4835 ГГц
    };

    channel_plan p;
    plan_channels(&ble, &p);

    printf("BLE @ 2.4 ГГц:\n");
    printf("  дрейф (1 бік):   %.0f кГц\n", p.drift_one_hz / 1e3);
    printf("  ширина слота:    %.2f МГц\n", p.slot_hz / 1e6);
    printf("  каналів влазить: %d\n", p.channels);
    printf("  накладні:        %.0f%%\n", p.overhead_frac * 100.0);
    return 0;
}
