static _Thread_local uint8_t scratch[64 * 1024];   /* спільний для ВСІХ з'єднань цього потоку */

static void on_readable(int ep, struct conn *c) {
    for (;;) {
        ssize_t n = recv(c->fd, scratch, sizeof scratch, 0);
        if (n == 0) { drop(ep, c); return; }              /* другий бік закрив запис */
        if (n < 0) {
            if (errno == EINTR)  continue;
            if (errno == EAGAIN) break;                   /* буфер ядра вичерпано */
            drop(ep, c); return;
        }
        if (feed(c, scratch, (size_t)n) < 0) { drop(ep, c); return; }
        /* scratch вільний уже тут: усе потрібне переписане у стан з'єднання */
    }
    if (flush(ep, c) < 0) drop(ep, c);
}
