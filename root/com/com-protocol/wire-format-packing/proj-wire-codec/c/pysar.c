typedef struct {
    uint8_t *p;     /* куди ляже наступний байт     */
    uint8_t *end;   /* за останнім байтом буфера    */
    bool     bad;   /* липко: місця не вистачило     */
} wr_t;

static void wr_init(wr_t *w, uint8_t *buf, size_t cap)
{
    w->p = buf; w->end = buf + cap; w->bad = false;
}

/* ЄДИНЕ місце, де кодек рахує межі. */
static uint8_t *wr_take(wr_t *w, size_t n)
{
    if (w->bad || (size_t)(w->end - w->p) < n) { w->bad = true; return NULL; }
    uint8_t *at = w->p;
    w->p += n;
    return at;
}
