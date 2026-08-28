static int pump_copy(struct conn *c)
{
    static char buf[64 * 1024];          /* спільний, стану не тримає */

    while (c->off < c->end) {
        ssize_t r = pread(c->file, buf, sizeof buf, c->off);
        if (r < 0) { if (errno == EINTR) continue; return -1; }
        if (r == 0) return -1;

        ssize_t sent = 0;
        while (sent < r) {
            ssize_t w = write(c->sock, buf + sent, r - sent);
            if (w < 0) {
                if (errno == EINTR) continue;
                if (errno == EAGAIN) { c->off += sent; return 0; }
                return -1;
            }
            sent += w;
        }
        c->off += r;
    }
    return 1;
}
