struct rx_result_t {
    uint8_t  data;          // зібраний байт
    bool     framing_error; // стоп був не «1»
    bool     parity_error;  // парність не збіглася
};

// bits[0] = старт, bits[1..8] = дані (D0..D7), bits[9] = парність, bits[10] = стоп
// (для 8N1 parity пропускаємо: передати mode = PAR_NONE і зсунути стоп на 9)
rx_result_t parse_frame(const uint8_t *bits, parity_t mode) {
    rx_result_t r = {0, false, false};

    uint8_t data = 0;
    for (int i = 0; i < 8; i++)
        data |= (bits[1 + i] & 1u) << i;   // D0 першим → лягає в біт 0
    r.data = data;

    int idx = 9;                            // наступна позиція після даних
    if (mode != PAR_NONE) {
        uint8_t expected = parity_bit(data, mode);
        if ((bits[idx] & 1u) != expected)
            r.parity_error = true;          // прийнятий P не збігся з перерахованим
        idx++;                              // стоп зсувається на 10
    }

    if ((bits[idx] & 1u) != 1u)             // стоп ЗОБОВ'ЯЗАНИЙ бути «1»
        r.framing_error = true;             // інакше межі кадру втрачено

    return r;
}
