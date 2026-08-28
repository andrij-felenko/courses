// Спроба передати радіо: важка дія, тож спершу питаємо сторожа.
// Якщо рейка просіла — НЕ передаємо (просадили б її ще глибше, в brownout),
// а відкладаємо кадр до відновлення напруги.
bool radio_try_send(const uint8_t *frame, uint16_t len) {
    if (!pwr_heavy_ok()) {          // сторож каже: рейці зараз зле
        queue_push(frame, len);     // відкласти кадр, не губити
        return false;               // передачу поки не робимо
    }
    radio_transmit(frame, len);     // рейка здорова — б'ємо в ефір
    return true;
}

// Виклик у головному циклі: коли живлення повернулось у OK — дораздати відкладене.
void radio_service(void) {
    while (pwr_heavy_ok() && !queue_empty()) {
        uint8_t  buf[MAX_FRAME];
        uint16_t n = queue_pop(buf);
        radio_transmit(buf, n);     // напруга дозволяє — випускаємо чергу
    }
}
