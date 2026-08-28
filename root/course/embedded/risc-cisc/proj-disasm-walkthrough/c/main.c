// Навмисне багато живих змінних одночасно — щоб забракло регістрів.
void stats(const uint16_t *a, uint8_t n,
           uint16_t *out_sum, uint16_t *out_min, uint16_t *out_max) {
    uint16_t s = 0, mn = 0xFFFF, mx = 0;
    for (uint8_t i = 0; i < n; i++) {
        uint16_t v = a[i];
        s  += v;
        if (v < mn) mn = v;
        if (v > mx) mx = v;
    }
    *out_sum = s; *out_min = mn; *out_max = mx;
}
