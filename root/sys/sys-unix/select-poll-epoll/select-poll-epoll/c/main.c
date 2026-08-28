int ep = epoll_create1(EPOLL_CLOEXEC);

struct epoll_event ev;
ev.events = EPOLLIN;
ev.data.fd = conn_fd;
epoll_ctl(ep, EPOLL_CTL_ADD, conn_fd, &ev);

struct epoll_event events[64];
for (;;) {
    int n = epoll_wait(ep, events, 64, -1);
    for (int i = 0; i < n; i++) {
        handle_data(events[i].data.fd);
    }
}
