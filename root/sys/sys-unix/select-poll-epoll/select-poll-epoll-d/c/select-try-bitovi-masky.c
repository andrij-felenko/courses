fd_set rfds;
struct timeval tv;

for (;;) {
    FD_ZERO(&rfds);                     /* мапу доводиться будувати щоразу заново */
    int maxfd = 0;
    for (int i = 0; i < nconn; i++) {
        FD_SET(conn[i].fd, &rfds);
        if (conn[i].fd > maxfd) maxfd = conn[i].fd;
    }
    tv.tv_sec = 1; tv.tv_usec = 0;      /* Linux змінює tv — теж щоразу наново */

    int n = select(maxfd + 1, &rfds, NULL, NULL, &tv);
    if (n < 0) { if (errno == EINTR) continue; die("select"); }

    for (int i = 0; i < nconn; i++)     /* хто саме готовий — знову шукаємо перебором */
        if (FD_ISSET(conn[i].fd, &rfds))
            handle(&conn[i]);
}
