/* Кодування довільного масиву з k 32-бітних чисел у єдиний 64-бітний код.
   Використовує послідовне лінійне згортання. */
bool cantor_tuple_encode32(const uint32_t *values, size_t k, uint64_t *out_code) {
    if (!values || k == 0 || !out_code) return false;
    if (k == 1) {
        *out_code = values[0];
        return true;
    }

    uint64_t current = values[0];
    for (size_t i = 1; i < k; ++i) {
        uint64_t w = current + values[i];
        if (w > 6074000999ULL) return false;
        current = (w * (w + 1)) / 2 + values[i];
    }

    *out_code = current;
    return true;
}

/* Декодування 64-бітного коду назад у масив з k 32-бітних чисел */
bool cantor_tuple_decode32(uint64_t code, size_t k, uint32_t *out_values) {
    if (!out_values || k == 0) return false;
    if (k == 1) {
        if (code > UINT32_MAX) return false;
        out_values[0] = (uint32_t)code;
        return true;
    }

    uint64_t current = code;
    for (size_t i = k - 1; i >= 1; --i) {
        if (current >= (UINT64_MAX / 8)) return false;
        uint64_t s = isqrt64_fast(8 * current + 1);
        uint64_t w = (s - 1) / 2;
        uint64_t base = (w * (w + 1)) / 2;
        uint64_t val = current - base;
        current = w - val;

        if (val > UINT32_MAX) return false;
        out_values[i] = (uint32_t)val;
    }

    if (current > UINT32_MAX) return false;
    out_values[0] = (uint32_t)current;
    return true;
}
