typedef struct { float lat, lon, alt; } fix;

typedef struct {
    arw win;
    fix cur;
    int has_fix;
} state_sink;

void on_datagram(state_sink *s, uint32_t seq, const fix *f)
{
    switch (arw_update(&s->win, seq)) {
    case ARW_NEW:                       /* свіжіше за все бачене — беремо */
        s->cur = *f;
        s->has_fix = 1;
        break;
    case ARW_LATE:                      /* законна, але вміст уже застарів */
    case ARW_DUPLICATE:
    case ARW_TOO_OLD:
        break;                          /* стан не чіпаємо */
    }
}
