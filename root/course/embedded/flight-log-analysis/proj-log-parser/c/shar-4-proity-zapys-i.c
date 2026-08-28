// Значення k-го поля (0-based) запису rec за кресленням f.
// Повертає 1 і кладе значення в *out; 0 — якщо поля з таким номером нема.
static int field_by_index(const MsgFormat *f, const uint8_t *rec,
                          int k, double *out) {
    const uint8_t *p = rec + 3;          // курсор: одразу за шапкою
    for (int i = 0; f->format[i]; i++) {
        double v;
        int sz = decode_field(f->format[i], p, &v);
        if (sz == 0) return 0;           // невідомий тип — далі йти наосліп не можна
        if (i == k) { *out = v; return 1; }
        p += sz;                         // крок = розмір поля (ПАСТКА 2 знята)
    }
    return 0;
}

// Номер поля з іменем `name` у рядку labels ("A,B,C") — або -1, якщо немає.
static int index_of_label(const char *labels, const char *name) {
    int idx = 0;
    const char *s = labels;
    size_t nlen = strlen(name);
    while (*s) {
        const char *comma = strchr(s, ',');
        size_t len = comma ? (size_t)(comma - s) : strlen(s);
        if (len == nlen && strncmp(s, name, nlen) == 0)
            return idx;                  // збіг рівно на межах поля
        if (!comma) break;
        s = comma + 1;
        idx++;
    }
    return -1;
}
