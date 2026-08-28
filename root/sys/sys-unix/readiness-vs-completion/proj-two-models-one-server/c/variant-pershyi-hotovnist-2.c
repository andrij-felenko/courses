static int flush(int ep, struct conn *c) {
    while (c->out_sent < c->out_len) {
        ssize_t n = send(c->fd, c->out + c->out_sent,
                         c->out_len - c->out_sent, MSG_NOSIGNAL);
        if (n > 0) { c->out_sent += (size_t)n; continue; } /* часткова передача — норма */
        if (errno == EINTR)  continue;
        if (errno == EAGAIN) return want_write(ep, c, 1);  /* ядро більше не бере */
        return -1;
    }
    c->out_len = c->out_sent = 0;
    return want_write(ep, c, 0);
}
