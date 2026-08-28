int connect_timeout(int fd, const struct sockaddr *addr, socklen_t alen, int ms) {
    int flags = fcntl(fd, F_GETFL, 0);
    fcntl(fd, F_SETFL, flags | O_NONBLOCK);

    if (connect(fd, addr, alen) == 0) {      /* устиг одразу — типово локальний хост */
        fcntl(fd, F_SETFL, flags);
        return 0;
    }
    if (errno != EINPROGRESS) return -1;     /* справжня помилка, а не «в процесі» */

    struct pollfd p = { .fd = fd, .events = POLLOUT };
    int r = poll(&p, 1, ms);
    if (r == 0) { errno = ETIMEDOUT; return -1; }
    if (r < 0)  return -1;

    int err = 0;                             /* готовність на запис ≠ успіх */
    socklen_t len = sizeof err;
    if (getsockopt(fd, SOL_SOCKET, SO_ERROR, &err, &len) < 0) return -1;
    if (err != 0) { errno = err; return -1; }

    fcntl(fd, F_SETFL, flags);
    return 0;
}
