// Кодує N відліків у N/2 байтів (по 4 біти на відлік).
// out мусить мати щонайменше (count + 1) / 2 байтів.
// Стан s зберігається МІЖ викликами — можна кодувати потік частинами.
void adpcm_encode(adpcm_state *s, const int16_t *in, uint8_t *out, int count) {
    int i = 0;
    while (i + 1 < count) {
        uint8_t lo = adpcm_encode_sample(s, in[i]);       // ПЕРШИЙ відлік
        uint8_t hi = adpcm_encode_sample(s, in[i + 1]);   // ДРУГИЙ відлік
        // стандарт IMA: перший код — у МОЛОДШІ біти, другий — у СТАРШІ
        *out++ = (uint8_t)((hi << 4) | (lo & 0x0f));
        i += 2;
    }
    // непарний останній відлік: молодший півбайт зайнятий, старший — 0
    if (i < count) {
        uint8_t lo = adpcm_encode_sample(s, in[i]);
        *out++ = (uint8_t)(lo & 0x0f);
    }
}
