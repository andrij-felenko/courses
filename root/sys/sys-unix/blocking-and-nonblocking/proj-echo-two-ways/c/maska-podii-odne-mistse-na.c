/* Маска = EPOLLIN плюс EPOLLOUT рівно тоді, коли є недописаний хвіст.
   epoll_ctl кличемо, лише якщо відповідь змінилася від минулого разу. */
static int arm(int ep, struct conn *c)
{
    int want = (c->out_off < c->out_len);
    if (want == c->want_write)
        return 0;

    struct epoll_event ev;
    memset(&ev, 0, sizeof ev);
    ev.events   = EPOLLIN | (want ? EPOLLOUT : 0);
    ev.data.ptr = c;

    if (epoll_ctl(ep, EPOLL_CTL_MOD, c->fd, &ev) < 0)
        return -1;

    c->want_write = want;
    return 0;
}
