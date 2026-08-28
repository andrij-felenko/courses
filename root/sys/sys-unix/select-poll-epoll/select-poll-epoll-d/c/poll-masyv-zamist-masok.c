struct pollfd *pfd = calloc(nconn, sizeof *pfd);
for (int i = 0; i < nconn; i++) {
    pfd[i].fd = conn[i].fd;
    pfd[i].events = POLLIN;             /* масив живий між обертами циклу */
}

for (;;) {
    int n = poll(pfd, nconn, 1000);
    if (n < 0) { if (errno == EINTR) continue; die("poll"); }

    for (int i = 0; i < nconn && n > 0; i++) {
        if (!pfd[i].revents) continue;
        n--;
        handle(&conn[i], pfd[i].revents);
    }
}
