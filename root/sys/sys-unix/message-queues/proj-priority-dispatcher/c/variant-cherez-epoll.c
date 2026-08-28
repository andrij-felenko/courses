int ep = epoll_create1(EPOLL_CLOEXEC);
struct epoll_event want = { .events = EPOLLIN, .data.fd = (int)q };
epoll_ctl(ep, EPOLL_CTL_ADD, (int)q, &want);

for (;;) {
    struct epoll_event got[8];
    int n = epoll_wait(ep, got, 8, -1);
    if (n == -1) { if (errno == EINTR) continue; perror("epoll_wait"); return 1; }

    for (int i = 0; i < n; i++)
        if (got[i].data.fd == (int)q) {
            drain(q, buf, attr.mq_msgsize);
            while (dispatch_one()) ;
        }
}
