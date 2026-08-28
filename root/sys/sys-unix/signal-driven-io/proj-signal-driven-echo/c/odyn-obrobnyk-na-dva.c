static void handle(int fd, int band)
{
    if (fd == listen_fd) { if (band & POLLIN) accept_all(); return; }
    if (!live[fd]) return;                         /* стале si_fd — вже закрили */

    if (band & POLLIN) {
        char buf[16384];
        for (;;) {
            ssize_t n = read(fd, buf, sizeof buf);
            if (n > 0)             { echo(fd, buf, (size_t) n); continue; }
            if (n == 0)            { drop(fd); return; }   /* закрив другий бік */
            if (errno == EINTR)      continue;
            if (errno == EAGAIN)     break;                /* буфер порожній */
            drop(fd); return;
        }
    }
    if (band & (POLLHUP | POLLERR)) drop(fd);
}

static void accept_all(void)
{
    for (;;) {
        int fd = accept4(listen_fd, NULL, NULL, SOCK_NONBLOCK);
        if (fd < 0) { if (errno == EINTR) continue; return; }   /* EAGAIN — усе */
        if (fd >= MAXFD) { close(fd); continue; }

        live[fd] = 1; nlive++;
        arm(fd);
        handle(fd, POLLIN);        /* дані могли прийти до озброєння */
    }
}
