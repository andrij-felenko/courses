/* Автомат станів одного з'єднання. 0 — живемо далі, -1 — закриваємо. */
static int on_readable(struct conn *c)
{
    for (;;) {
        if (c->phase == PH_HEADER) {
            ssize_t k = read(c->fd, c->hdr + c->hdr_got, sizeof c->hdr - c->hdr_got);
            if (k == 0) return -1;                    /* інший бік закрив */
            if (k < 0) {
                if (errno == EINTR) continue;
                if (errno == EAGAIN || errno == EWOULDBLOCK) return 0;
                return -1;
            }
            c->hdr_got += (size_t)k;
            if (c->hdr_got < sizeof c->hdr)
                continue;                             /* заголовок ще не цілий */

            uint32_t len;
            memcpy(&len, c->hdr, sizeof len);
            len = ntohl(len);
            if (len > MAX_BODY) return -1;

            c->body_len = len;
            c->body_got = 0;
            if (len > 0) {
                c->body = malloc(len);
                if (c->body == NULL) return -1;
            }
            c->phase = PH_BODY;
            continue;              /* ← без цього рядка з'єднання зависає, див. пастку 1 */
        }

        while (c->body_got < c->body_len) {
            ssize_t k = read(c->fd, c->body + c->body_got, c->body_len - c->body_got);
            if (k == 0) return -1;
            if (k < 0) {
                if (errno == EINTR) continue;
                if (errno == EAGAIN || errno == EWOULDBLOCK) return 0;
                return -1;
            }
            c->body_got += (size_t)k;
        }

        /* повідомлення ціле — відповідь у чергу й одразу пробуємо відправити */
        uint32_t be = htonl((uint32_t)c->body_len);
        if (out_push(c, &be, sizeof be) < 0)       return -1;
        if (out_push(c, c->body, c->body_len) < 0) return -1;
        if (out_flush(c) < 0)                      return -1;

        free(c->body);
        c->body     = NULL;
        c->body_len = 0;
        c->body_got = 0;
        c->hdr_got  = 0;
        c->phase    = PH_HEADER;
    }
}
