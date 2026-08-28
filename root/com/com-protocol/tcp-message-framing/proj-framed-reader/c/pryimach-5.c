fr_status conn_on_readable(struct conn *c)
{
    for (;;) {
        if (!reserve(c, c->have + 1)) return FR_NOMEM;   /* місце є завжди... */
        size_t room = c->cap - c->have;                  /* ...і воно > 0 */

        ssize_t n = recv(c->fd, c->buf + c->have, room, 0);

        if (n < 0) {
            if (errno == EINTR) continue;                /* перервано сигналом */
            if (errno == EAGAIN || errno == EWOULDBLOCK)
                return FR_OK;                            /* черга прийому порожня */
            return FR_IO;
        }
        if (n == 0)                                      /* інший бік закрив напрямок */
            return c->have == 0 ? FR_EOF : FR_TRUNCATED;

        c->have += (size_t)n;

        fr_status st = parse_all(c);
        if (st != FR_OK) return st;

        if ((size_t)n < room) return FR_OK;   /* прочитали менше, ніж просили */
    }
}

void conn_close(struct conn *c)
{
    free(c->buf);
    c->buf = NULL;
    c->cap = c->have = 0;
}
