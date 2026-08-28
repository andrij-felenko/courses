static volatile uint32_t g_due;   /* борг: скільки гранул винні */

static void due_add(uint32_t n)
{
    uint32_t v;
    do { v = __LDREXW(&g_due); } while (__STREXW(v + n, &g_due) != 0u);
}

static uint32_t due_take(uint32_t max)
{
    uint32_t v, got;
    do {
        v = __LDREXW(&g_due);
        got = (v < max) ? v : max;
        if (got == 0u) { __CLREX(); return 0u; }
    } while (__STREXW(v - got, &g_due) != 0u);
    return got;
}
