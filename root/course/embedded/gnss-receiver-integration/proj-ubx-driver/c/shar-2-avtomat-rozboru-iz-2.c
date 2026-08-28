// Викликається з gnss_poll щоразу. Якщо ми посеред пакета, а байтів
// немає довше за поріг — примусово синхронізуємось наново.
#define UBX_IDLE_MS  20   // на 115200 бод пакет із 92 байтів іде <10 мс; 20 — із запасом

static void ubx_check_idle(uint32_t now_ms) {
    if (P.state != UST_SYNC1 &&
        (uint32_t)(now_ms - P.last_byte_ms) > UBX_IDLE_MS) {
        ubx_reset();        // напівпакет протух — викидаємо, не зависаємо
    }
}
