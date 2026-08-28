    // ── Wi-Fi 2.4 ГГц: канал 20 МГц, той самий кварц і смуга ─────────────
    radio_spec wifi = {
        .carrier_hz   = 2.437e9,    // центр діапазону (≈ канал 6)
        .ppm          = 20.0,       // Wi-Fi радіо точніше, ±20 ppm
        .signal_bw_hz = 20.0e6,     // канал 802.11 завширшки 20 МГц
        .guard_hz     = 5.0e6,      // міжканальний зазор до сусіда
        .rel_speed_ms = 0.0,
        .band_hz      = 83.5e6,
    };

    channel_plan w;
    plan_channels(&wifi, &w);

    printf("\nWi-Fi @ 2.4 ГГц (канал 20 МГц):\n");
    printf("  дрейф (1 бік):   %.0f кГц\n", w.drift_one_hz / 1e3);
    printf("  ширина слота:    %.2f МГц\n", w.slot_hz / 1e6);
    printf("  каналів влазить: %d\n", w.channels);
