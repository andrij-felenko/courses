static void arm(int ep, struct conn *c, int want_out)
{
    struct epoll_event ev = {
        .events   = EPOLLIN | EPOLLRDHUP | (want_out ? EPOLLOUT : 0),
        .data.ptr = c,
    };
    epoll_ctl(ep, EPOLL_CTL_MOD, c->sock, &ev);
}

for (;;) {
    int k = epoll_wait(ep, evs, MAXEV, -1);
    for (int i = 0; i < k; i++) {
        struct conn *c = evs[i].data.ptr;

        int r = pump(c);
        if (r == 0)
            arm(ep, c, 1);       /* черга повна — чекаємо місця */
        else if (r == 1)
            finish(c);           /* arm(ep, c, 0) або закриття */
        else
            drop(c);
    }
}
