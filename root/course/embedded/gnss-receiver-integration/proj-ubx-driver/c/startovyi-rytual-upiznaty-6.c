// Публічний старт драйвера. Викликати раз, поки апарат на землі.
bool gnss_init(void) {
    const uint32_t bauds[] = { 9600, 115200 };   // заводська й наша цільова
    for (int i = 0; i < 2; i++) {
        uart_set_baud(bauds[i]);
        ubx_reset();
        // Запит версії: payload порожній, відповідь MON-VER зловить dispatch.
        g_gen = GEN_UNKNOWN;
        ubx_send(UBX_CLS_MON, UBX_MON_VER, NULL, 0);
        uint32_t t0 = millis();
        while ((uint32_t)(millis() - t0) < 400) {
            gnss_poll(millis());
            if (g_gen != GEN_UNKNOWN) break;      // dispatch викликав detect_from_monver
        }
        if (g_gen != GEN_UNKNOWN) break;          // відповів на цій швидкості
    }
    if (g_gen == GEN_UNKNOWN) return false;       // модуль не озвався — залізо/дроти

    bool ok = (g_gen == GEN_M9_M10) ? configure_m9_m10() : configure_m8();
    return ok;
}
