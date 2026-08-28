// Медіана з N вимірів — стійка до поодиноких викидів дзвону/джитера.
static int cmp_u32(const void *a, const void *b) {
    uint32_t x = *(const uint32_t*)a, y = *(const uint32_t*)b;
    return (x > y) - (x < y);
}

uint32_t measure_dead_time_median(uint8_t n)
{
    uint32_t buf[16];
    if (n > 16) n = 16;
    uint8_t got = 0;
    for (uint8_t i = 0; i < n; i++) {
        uint32_t v = measure_dead_time_ns();
        if (v > 0) buf[got++] = v;      // 0 = невдалий вимір, відкидаємо
        delay_us(500);                   // ключ охолонути/навантаженню розрядитись
    }
    if (got == 0) return 0;              // жодного чесного виміру — діагностика
    qsort(buf, got, sizeof(buf[0]), cmp_u32);
    return buf[got / 2];                 // медіана
}
