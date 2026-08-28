// GATHER: зібрати розкидані сегменти в один суцільний буфер.
// ⚠ addr мусять бути ВІРТУАЛЬНІ (розіменовні). Повертає скільки зібрано.
size_t sg_gather(const struct sg_list *sg, void *dst, size_t cap) {
    unsigned char *d = (unsigned char *)dst;
    size_t done = 0;
    for (int i = 0; i < sg->n && done < cap; i++) {
        size_t take = sg->seg[i].len;
        if (take > cap - done) take = cap - done;      // не вилізти за dst
        if (take == 0) continue;                       // memcpy з NULL — навіть на 0 Б
        memcpy(d + done, (const void *)sg->seg[i].addr, take);
        done += take;
    }
    return done;
}

// SCATTER: розкласти суцільний буфер по сегментах.
// ⚠ addr мусять бути ВІРТУАЛЬНІ. Повертає скільки розклано.
size_t sg_scatter(const struct sg_list *sg, const void *src, size_t len) {
    const unsigned char *s = (const unsigned char *)src;
    size_t done = 0;
    for (int i = 0; i < sg->n && done < len; i++) {
        size_t put = sg->seg[i].len;
        if (put > len - done) put = len - done;        // не вичерпати src
        if (put == 0) continue;
        memcpy((void *)sg->seg[i].addr, s + done, put);
        done += put;
    }
    return done;
}
