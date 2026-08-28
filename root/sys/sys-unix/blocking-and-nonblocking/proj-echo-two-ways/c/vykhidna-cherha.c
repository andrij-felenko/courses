/* Додає дані у вихідну чергу. -1 — черга переросла стелю або скінчилася пам'ять. */
static int out_push(struct conn *c, const void *data, size_t n)
{
    if (n == 0)
        return 0;

    if (c->out_off > 0) {          /* викидаємо з початку те, що вже пішло */
        memmove(c->out, c->out + c->out_off, c->out_len - c->out_off);
        c->out_len -= c->out_off;
        c->out_off = 0;
    }
    if (c->out_len + n > MAX_OUT)
        return -1;

    if (c->out_len + n > c->out_cap) {
        size_t cap = c->out_cap ? c->out_cap : 4096;
        while (cap < c->out_len + n)
            cap *= 2;
        char *p = realloc(c->out, cap);
        if (p == NULL)
            return -1;
        c->out = p;
        c->out_cap = cap;
    }
    memcpy(c->out + c->out_len, data, n);
    c->out_len += n;
    return 0;
}

/* Пише, скільки візьмуть. 0 — гаразд (хвіст міг лишитись), -1 — з'єднання мертве. */
static int out_flush(struct conn *c)
{
    while (c->out_off < c->out_len) {
        ssize_t k = write(c->fd, c->out + c->out_off, c->out_len - c->out_off);
        if (k > 0) {
            c->out_off += (size_t)k;
            continue;
        }
        if (k < 0 && errno == EINTR)
            continue;
        if (k < 0 && (errno == EAGAIN || errno == EWOULDBLOCK))
            return 0;               /* буфер передачі повний — чекаємо на EPOLLOUT */
        return -1;
    }
    c->out_off = 0;
    c->out_len = 0;
    return 0;
}
