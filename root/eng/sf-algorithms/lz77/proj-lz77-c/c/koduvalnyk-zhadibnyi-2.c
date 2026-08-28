// Кодує src[0..n) у масив трійок out (місткістю out_cap). Повертає кількість трійок.
size_t lz77_encode(const uint8_t *src, size_t n, Triple *out, size_t out_cap) {
    size_t pos = 0, count = 0;

    while (pos < n && count < out_cap) {
        size_t off;
        size_t len = find_match(src, n, pos, &off);

        if (len < MIN_LEN) {            // збігу нема (або закороткий) → лише свіжий байт
            out[count].offset   = 0;
            out[count].length   = 0;
            out[count].next     = src[pos];
            out[count].has_next = 1;
            pos += 1;
        } else {                        // є вигідний збіг → посилання + свіжий байт за ним
            out[count].offset = (uint16_t)off;
            out[count].length = (uint16_t)len;
            pos += len;                 // перестрибуємо весь збіг
            if (pos < n) {              // ...і дописуємо наступний свіжий байт
                out[count].next     = src[pos];
                out[count].has_next = 1;
                pos += 1;
            } else {
                out[count].has_next = 0; // збіг сягнув самого кінця — свіжого байта нема
            }
        }
        count++;
    }
    return count;
}
