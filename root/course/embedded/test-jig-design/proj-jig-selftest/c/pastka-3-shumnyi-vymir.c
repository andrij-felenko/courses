// Медіана масиву відліків: посортувати й узяти середній.
// N невеликий (16–32), тож звичайне сортування вставками — цілком доречне.
static int cmp_u16(const void *a, const void *b) {
    uint16_t x = *(const uint16_t *)a, y = *(const uint16_t *)b;
    return (x > y) - (x < y);
}

uint16_t adc_read_median(uint8_t channel, uint16_t *scratch, unsigned n) {
    for (unsigned i = 0; i < n; i++) scratch[i] = adc_read_raw(channel);
    qsort(scratch, n, sizeof(scratch[0]), cmp_u16);
    return scratch[n / 2];
}
