static uint32_t g_acc;

/* з переривання таймера 1 кГц */
static uint32_t scrub_credit(void)
{
    uint32_t n = 0;
    g_acc += GRANULES;                  /* 65536 */
    while (g_acc >= TICKS_PER_PASS) {   /* 60000 */
        g_acc -= TICKS_PER_PASS;
        n++;
    }
    return n;                           /* 1 або 2 — і в середньому рівно 1.0923 */
}
