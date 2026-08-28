// зовнішня межа: дані можуть бути биті → ЗАСТАВА, м'яка реакція
esp_err_t on_uart_frame(const uint8_t *buf, size_t len) {
    if (buf == NULL || len < FRAME_HEADER_SIZE)
        return ESP_ERR_INVALID_SIZE;          // законна біда — відкидаємо
    /* ... */
}

// внутрішній інваріант: цього не буває ніколи → ASSERT
void ring_push(ring_t *r, uint8_t v) {
    assert(r->head < r->size);                // якщо ні — баг у нашому коді
    r->buf[r->head++] = v;
}
