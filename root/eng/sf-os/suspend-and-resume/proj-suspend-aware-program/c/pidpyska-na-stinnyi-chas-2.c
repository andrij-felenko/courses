for (;;) {
    struct epoll_event ev[8];
    int n = epoll_wait(ep, ev, 8, timeout_ms());
    if (n < 0 && errno == EINTR)
        continue;

    /* Перше після будь-якого повернення з очікування: чи ми спали? */
    int64_t now_slept = slept_ns();
    int64_t gap_ms = (now_slept - last_slept) / 1000000;
    last_slept = now_slept;
    if (gap_ms > 1000)
        probe_link(link);              /* сокет під підозрою */

    for (int i = 0; i < n; i++) {
        uint64_t ticks;
        int fd = ev[i].data.fd;

        if (fd == alarm_fd) {
            if (read(fd, &ticks, sizeof ticks) == (ssize_t)sizeof ticks)
                poll_sensor(ticks);    /* ticks > 1 — періоди пропущено */
        } else if (fd == wall_fd) {
            if (read(fd, &ticks, sizeof ticks) < 0 && errno == ECANCELED) {
                reschedule_wallclock_jobs();
                arm_wallwatch(fd);     /* поновлюємо підписку */
            }
        } else if (fd == link) {
            serve_link(fd);
        }
    }
}
