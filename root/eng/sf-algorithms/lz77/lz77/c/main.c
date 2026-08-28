// Декодер LZ77: розгортає потік трійок (offset, length, next) назад у дані.
// out — буфер виходу, який заразом служить «словником»: копіюємо з нього ж.
size_t lz77_decode(const Triple *in, size_t n_triples, uint8_t *out) {
    size_t o = 0;                       // скільки символів уже відновлено
    for (size_t i = 0; i < n_triples; i++) {
        size_t off = in[i].offset;      // на скільки назад
        size_t len = in[i].length;      // скільки копіювати
        // копіюємо len символів із уже відновленого хвоста (по одному —
        // це важливо: збіг може накладатися сам на себе, див. нижче)
        for (size_t k = 0; k < len; k++)
            out[o + k] = out[o - off + k];
        o += len;
        if (in[i].has_next)             // і дописуємо свіжий символ, якщо він є
            out[o++] = in[i].next;
    }
    return o;
}
