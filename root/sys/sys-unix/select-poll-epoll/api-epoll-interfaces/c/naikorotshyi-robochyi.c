#include <sys/epoll.h>
#include <errno.h>
#include <stdio.h>

int ep = epoll_create1(EPOLL_CLOEXEC);
if (ep < 0) { perror("epoll_create1"); return 1; }

struct epoll_event ev = { .events = EPOLLIN | EPOLLRDHUP, .data.fd = fd };
if (epoll_ctl(ep, EPOLL_CTL_ADD, fd, &ev) < 0) { perror("epoll_ctl"); return 1; }

struct epoll_event out[64];
for (;;) {
    int n = epoll_wait(ep, out, 64, -1);
    if (n < 0) {
        if (errno == EINTR) continue;      /* сигнал, не помилка */
        perror("epoll_wait"); break;
    }
    for (int i = 0; i < n; i++) {
        uint32_t e = out[i].events;
        if (e & (EPOLLERR | EPOLLHUP)) { drop(out[i].data.fd); continue; }
        if (e & EPOLLIN)  on_readable(out[i].data.fd);   /* дочитати залишок */
        if (e & EPOLLOUT) on_writable(out[i].data.fd);
        if (e & EPOLLRDHUP) drop(out[i].data.fd);        /* аж після того, як залишок дочитано */
    }
}
