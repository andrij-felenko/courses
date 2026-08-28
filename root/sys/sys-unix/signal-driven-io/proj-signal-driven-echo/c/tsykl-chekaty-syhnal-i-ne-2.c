static void rescan(void)
{
    static struct pollfd pf[MAXFD];
    int n = 0;

    pf[n].fd = listen_fd; pf[n].events = POLLIN; n++;
    for (int fd = 0; fd < MAXFD; fd++)
        if (live[fd]) { pf[n].fd = fd; pf[n].events = POLLIN; n++; }

    if (poll(pf, (nfds_t) n, 0) <= 0) return;
    for (int i = 0; i < n; i++)
        if (pf[i].revents) handle(pf[i].fd, pf[i].revents);
}
