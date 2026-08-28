// Викликається періодично, поки список неповний:
void param_download_tick(void) {
    if (total == 0) return;                       // ще не почали
    if (have >= total) { on_download_done(); return; }
    if (now_ms() - last_rx_ms < PARAM_TIMEOUT_MS) return;   // ще йдуть

    // потік завмер, але маємо не все — перепитуємо діри по одній
    for (uint16_t i = 0; i < total; i++) {
        if (!got[i]) {
            send_param_request_read(/*index=*/ i);
        }
    }
    last_rx_ms = now_ms();                         // дамо їм час відповісти
}
