static void task_ready(task *t)
{
    uint64_t ticks;
    if (read(t->fd, &ticks, sizeof ticks) != (ssize_t)sizeof ticks) {
        if (errno == EAGAIN) return;          /* хибне пробудження — не помилка */
        perror("read(timerfd)");
        return;
    }

    struct timespec now;
    clock_gettime(CLOCK_MONOTONIC, &now);

    uint64_t n = t->fired + ticks;            /* номер останнього строку, що настав */
    struct timespec nominal = ts_add_ns(t->origin, (int64_t)n * t->period_ns);
    int64_t late = ts_sub_ns(now, nominal);
    if (late > t->worst_late_ns) t->worst_late_ns = late;

    if (t->policy == CATCH_UP)
        for (uint64_t k = 0; k < ticks; k++) t->run();
    else {
        t->skipped += ticks - 1;
        t->run();
    }
    t->fired = n;
}

int main(void)
{
    static task tasks[] = {
        { .name = "датчик",     .period_ns =   20000000LL, .policy = SKIP,     .run = poll_sensor },
        { .name = "телеметрія", .period_ns =  200000000LL, .policy = SKIP,     .run = send_telemetry },
        { .name = "журнал",     .period_ns = 5000000000LL, .policy = CATCH_UP, .run = rotate_log },
    };
    int epfd = epoll_create1(EPOLL_CLOEXEC);

    struct timespec origin;
    clock_gettime(CLOCK_MONOTONIC, &origin);        /* спільний нуль фази для всіх задач */
    for (size_t i = 0; i < sizeof tasks / sizeof *tasks; i++)
        task_arm(&tasks[i], origin, epfd);

    for (;;) {
        struct epoll_event ev[16];
        int n = epoll_wait(epfd, ev, 16, -1);
        if (n < 0) { if (errno == EINTR) continue; break; }
        for (int i = 0; i < n; i++)
            task_ready(ev[i].data.ptr);             /* у справжній службі в data лежить */
    }                                               /* мічена структура: тут таймер, там сокет */
}
