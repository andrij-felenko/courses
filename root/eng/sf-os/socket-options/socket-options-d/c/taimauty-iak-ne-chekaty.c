static long now_ms(void) {
    struct timespec ts;
    clock_gettime(CLOCK_MONOTONIC, &ts);
    return ts.tv_sec * 1000L + ts.tv_nsec / 1000000L;
}

/* прочитати рівно need байтів, витративши на все не більше budget_ms */
int recv_exact_deadline(int fd, void *buf, size_t need, long budget_ms) {
    long deadline = now_ms() + budget_ms;
    size_t got = 0;

    while (got < need) {
        long left = deadline - now_ms();
        if (left <= 0) { errno = ETIMEDOUT; return -1; }

        struct timeval tv = { .tv_sec = left / 1000,
                              .tv_usec = (left % 1000) * 1000 };
        if (setsockopt(fd, SOL_SOCKET, SO_RCVTIMEO, &tv, sizeof tv) < 0)
            return -1;

        ssize_t n = recv(fd, (char *)buf + got, need - got, 0);
        if (n == 0) { errno = ECONNRESET; return -1; }  /* інший бік закрив */
        if (n < 0) {
            if (errno == EINTR) continue;               /* сигнал — не помилка */
            return -1;                                  /* EAGAIN — час вичерпано */
        }
        got += (size_t)n;
    }
    return 0;
}
