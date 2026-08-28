int fd = sd_bus_get_fd(bus);
struct epoll_event ev = { .data.fd = fd };
epoll_ctl(epfd, EPOLL_CTL_ADD, fd, &ev);

for (;;) {
    while ((r = sd_bus_process(bus, NULL)) > 0)   /* вичерпати чергу до нуля */
        ;
    if (r < 0) break;

    int want = sd_bus_get_events(bus);            /* POLLIN та/або POLLOUT */
    ev.events = (want & POLLIN  ? EPOLLIN  : 0)
              | (want & POLLOUT ? EPOLLOUT : 0);
    epoll_ctl(epfd, EPOLL_CTL_MOD, fd, &ev);      /* маска МІНЛИВА: є що слати — POLLOUT */

    uint64_t deadline;                            /* АБСОЛЮТНИЙ строк, CLOCK_MONOTONIC, мкс */
    sd_bus_get_timeout(bus, &deadline);
    int ms = -1;
    if (deadline != UINT64_MAX) {
        struct timespec ts;
        clock_gettime(CLOCK_MONOTONIC, &ts);
        uint64_t now = (uint64_t)ts.tv_sec * 1000000 + ts.tv_nsec / 1000;
        ms = deadline > now ? (int)((deadline - now + 999) / 1000) : 0;
    }
    epoll_wait(epfd, out, N, ms);                 /* тут же прокидаються й ваші дескриптори */
}
