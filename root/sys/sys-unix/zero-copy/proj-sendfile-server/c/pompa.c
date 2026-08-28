static int pump(struct conn *c)
{
    if (c->raw)
        return pump_copy(c);

    while (c->off < c->end) {
        size_t want = (size_t)(c->end - c->off);
        if (want > CHUNK)
            want = CHUNK;

        ssize_t n = sendfile(c->sock, c->file, &c->off, want);

        if (n > 0)
            continue;                     /* ядро вже посунуло c->off */
        if (n == 0)
            return -1;                    /* файл зрізали під нами */
        if (errno == EINTR)
            continue;
        if (errno == EAGAIN)
            return 0;                     /* черга повна — вихід, не сон */
        if (errno == EINVAL || errno == ENOSYS) {
            c->raw = 1;
            return pump_copy(c);
        }
        return -1;                        /* EPIPE, ECONNRESET, EIO… */
    }
    return 1;
}
