// LZW-декодування. Єдина тонкість — гілка code == next (випадок cScSc).
void lzw_decode(BitReader *br, uint8_t *dst, size_t cap) {
    dict_reset();
    int next = FIRST, width = 9;
    size_t o = 0;

    int prev = -1;
    uint8_t first_of_prev = 0;
    for (;;) {
        int code = bits_get(br, width);
        if (code == END) break;
        if (code == CLEAR) {                 // скидання — почати наново
            dict_reset(); next = FIRST; width = 9; prev = -1;
            continue;
        }

        uint8_t buf[MAXCODE + 1];            // рядок збираємо з ХВОСТА
        int len;
        if (code < next) {                   // код є — звичайний випадок
            len = dict_emit(code, buf);      // розкласти запис у байти
        } else if (code == next && prev != -1) {  // cScSc: код = наступний-вільний
            len = dict_emit(prev, buf);      // це prev + перший байт prev
            buf[len++] = first_of_prev;
        } else {
            return;                          // зіпсований потік
        }

        for (int k = 0; k < len; k++) dst[o++] = buf[k];   // вивести рядок
        uint8_t first_of_cur = buf[0];

        if (prev != -1) {                    // додати prev + перший байт поточного
            dict_insert(prev, first_of_cur, next++);
            if (next > (1 << width) && width < MAXBITS) width++;
        }
        prev = (code < next - 1) ? code : next - 1;   // новий prev (його номер)
        first_of_prev = first_of_cur;
    }
}
