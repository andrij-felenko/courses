int tfd = timerfd_create(CLOCK_MONOTONIC, TFD_NONBLOCK | TFD_CLOEXEC);
struct itimerspec its = { .it_value    = { .tv_sec = 0, .tv_nsec = 250000000 },
                          .it_interval = { .tv_sec = 0, .tv_nsec = 250000000 } };
timerfd_settime(tfd, 0, &its, NULL);

struct epoll_event ev = { .events = EPOLLIN, .data.fd = tfd };
epoll_ctl(ep, EPOLL_CTL_ADD, tfd, &ev);

/* у циклі подій, поряд із сокетами: */
uint64_t ticks;
if (read(tfd, &ticks, sizeof ticks) == sizeof ticks) {
    /* ticks — скільки спрацювань набігло від минулого читання */
}
