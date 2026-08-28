#define OSR  32              // бітів PDM на один PCM-відлік

// Перетворює count відліків PCM у count*OSR бітів, спакованих по 8 у байт.
// out мусить мати щонайменше count*OSR/8 байтів.
// Стан s зберігається МІЖ викликами — потік можна гнати частинами.
void pcm_to_pdm(pdm_state *s, const int16_t *in, uint8_t *out, int count) {
    int bit_pos = 0;                 // позиція біта в поточному байті (0..7)
    uint8_t acc = 0;                 // збираємо 8 бітів, тоді пишемо байт

    for (int i = 0; i < count; i++) {
        int16_t sample = in[i];
        // передискретизування: той самий відлік OSR разів у формувач
        for (int k = 0; k < OSR; k++) {
            bool bit = pdm_step(s, sample);
            acc = (uint8_t)((acc << 1) | (bit ? 1 : 0));   // MSB першим
            if (++bit_pos == 8) {
                *out++ = acc;
                acc = 0;
                bit_pos = 0;
            }
        }
    }
    // якщо назбирали неповний байт — добиваємо (у бойовому коді краще
    // тримати count*OSR кратним 8, щоб хвіст не рвав потік)
    if (bit_pos != 0) {
        acc <<= (8 - bit_pos);
        *out++ = acc;
    }
}
