// Розгортає масив трійок назад у байти. out — вихідний буфер (він-таки словник).
// Повертає кількість відновлених байтів.
size_t lz77_decode(const Triple *in, size_t count, uint8_t *out) {
    size_t o = 0;
    for (size_t i = 0; i < count; i++) {
        size_t off = in[i].offset;
        size_t len = in[i].length;

        // КЛЮЧОВЕ: копіюємо по одному байту зліва направо.
        // Якщо off < len, ми дописуємо байти, на які тут-таки посилаємось —
        // так одна трійка відтворює довгу серію (накладний збіг).
        for (size_t k = 0; k < len; k++) {
            out[o] = out[o - off];
            o++;
        }
        if (in[i].has_next)
            out[o++] = in[i].next;
    }
    return o;
}
