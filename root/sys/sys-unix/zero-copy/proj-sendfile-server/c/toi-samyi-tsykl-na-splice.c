static int pump_splice(struct conn *c)
{
    for (;;) {
        if (c->in_pipe == 0 && c->off < c->end) {
            size_t want = (size_t)(c->end - c->off);
            if (want > 64 << 10)
                want = 64 << 10;                  /* місткість каналу */

            ssize_t n = splice(c->file, &c->off, c->pipe[1], NULL,
                               want, SPLICE_F_MORE);
            if (n < 0) { if (errno == EINTR) continue; return -1; }
            if (n == 0) return -1;
            c->in_pipe += (size_t)n;
        }

        if (c->in_pipe == 0)
            return 1;                             /* усе віддано */

        ssize_t m = splice(c->pipe[0], NULL, c->sock, NULL, c->in_pipe,
                           SPLICE_F_MORE | SPLICE_F_NONBLOCK);
        if (m < 0) {
            if (errno == EINTR) continue;
            if (errno == EAGAIN) return 0;
            return -1;
        }
        c->in_pipe -= (size_t)m;
    }
}
