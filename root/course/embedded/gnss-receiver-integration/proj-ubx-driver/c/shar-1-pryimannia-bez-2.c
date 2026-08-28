// Викликається з головного циклу якомога частіше. Вичерпує кільце,
// не блокуючи: скільки байтів є — стільки й з'їдає, і повертається.
void gnss_poll(uint32_t now_ms) {
    while (rx_tail != rx_head) {
        uint8_t b = rx_ring[rx_tail];
        rx_tail = (rx_tail + 1) & (RX_RING - 1);
        ubx_feed(b, now_ms);        // згодувати автомату один байт
    }
    ubx_check_idle(now_ms);         // таймер міжбайтового простою (нижче)
}
