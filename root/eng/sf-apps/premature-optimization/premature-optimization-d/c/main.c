// Просто: очевидно, правильно, правиться за секунди.
uint32_t sum_samples(const uint16_t *buf, size_t n) {
    uint32_t s = 0;
    for (size_t i = 0; i < n; i++)
        s += buf[i];
    return s;
}

// "Оптимізовано" наосліп: ручне розгортання по 4, заради швидкості,
// якої ніхто не міряв. Читати важче, межу n треба обробляти окремо,
// баг у "хвості" (n не кратне 4) ховається саме тут.
uint32_t sum_samples_fast(const uint16_t *buf, size_t n) {
    uint32_t s = 0;
    size_t i = 0;
    for (; i + 4 <= n; i += 4)
        s += buf[i] + buf[i+1] + buf[i+2] + buf[i+3];
    for (; i < n; i++)          // окремий хвіст — новий шанс помилитися
        s += buf[i];
    return s;
}
