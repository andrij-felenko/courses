/* Гарантує cap >= want. Вище стелі кадру не росте НІКОЛИ. */
static int reserve(struct conn *c, size_t want)
{
    const size_t ceiling = (size_t)HDR + MAX_FRAME;
    if (want > ceiling) return 0;      /* поза специфікацією — не наша справа */
    if (want <= c->cap)  return 1;

    size_t cap = c->cap ? c->cap : (size_t)BUF_MIN;
    while (cap < want) cap *= 2;
    if (cap > ceiling) cap = ceiling;

    uint8_t *p = realloc(c->buf, cap);
    if (!p) return 0;
    c->buf = p;
    c->cap = cap;
    return 1;
}
