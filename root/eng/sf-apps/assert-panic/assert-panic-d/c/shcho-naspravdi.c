// Зразок розташування тверджень за контрактом
size_t ring_push(ring_t *r, const uint8_t *data, size_t n) {
    // ПЕРЕДУМОВИ — борг викликача (вхідні assert)
    assert(r != NULL);
    assert(data != NULL || n == 0);
    assert(r->head < r->cap && r->tail < r->cap);   // інваріант на вході

    size_t written = 0;
    while (written < n && ring_free(r) > 0) {
        r->buf[r->head] = data[written++];
        r->head = (r->head + 1) % r->cap;
    }

    // ПОСТУМОВА / ІНВАРІАНТ — борг функції (вихідні assert)
    assert(r->head < r->cap);                        // голова лишилась у межах
    assert(written <= n);
    return written;
}
