// Безблокувальне читання періоду через лічильник версії (seqlock-стиль).
static uint64_t seqlock_load_period(void)
{
    uint64_t v; uint32_t s1, s2;
    do {
        s1 = g_seq;            // версія до читання
        v  = g_period;         // саме значення
        s2 = g_seq;            // версія після читання
    } while (s1 != s2);        // ISR втрутився посередині → читаємо знову
    return v;
}
