static void accept_all(int ep, int ls)
{
    for (;;) {
        int fd = accept4(ls, NULL, NULL, SOCK_NONBLOCK);   /* з Linux 2.6.28 */
        if (fd < 0) {
            if (errno == EINTR) continue;
            return;      /* EAGAIN — черга порожня; EMFILE — скінчилися дескриптори */
        }
        struct conn *c = conn_new(fd);
        if (c == NULL) { close(fd); continue; }

        struct epoll_event ev;
        memset(&ev, 0, sizeof ev);
        ev.events   = EPOLLIN;
        ev.data.ptr = c;
        if (epoll_ctl(ep, EPOLL_CTL_ADD, fd, &ev) < 0) {
            close(fd);
            free(c);
        }
    }
}

int main(void)
{
    signal(SIGPIPE, SIG_IGN);

    int ls = socket(AF_INET, SOCK_STREAM | SOCK_NONBLOCK, 0);  /* з Linux 2.6.27 */
    if (ls < 0) { perror("socket"); return 1; }

    int one = 1;
    setsockopt(ls, SOL_SOCKET, SO_REUSEADDR, &one, sizeof one);

    struct sockaddr_in a;
    memset(&a, 0, sizeof a);
    a.sin_family      = AF_INET;
    a.sin_addr.s_addr = htonl(INADDR_LOOPBACK);
    a.sin_port        = htons(PORT);

    if (bind(ls, (struct sockaddr *)&a, sizeof a) < 0) { perror("bind");   return 1; }
    if (listen(ls, 128) < 0)                           { perror("listen"); return 1; }

    int ep = epoll_create1(0);
    if (ep < 0) { perror("epoll_create1"); return 1; }

    struct epoll_event ev;
    memset(&ev, 0, sizeof ev);
    ev.events   = EPOLLIN;
    ev.data.ptr = NULL;                       /* NULL — позначка слухаючого сокета */
    if (epoll_ctl(ep, EPOLL_CTL_ADD, ls, &ev) < 0) { perror("epoll_ctl"); return 1; }

    struct epoll_event evs[MAX_EV];
    for (;;) {
        int n = epoll_wait(ep, evs, MAX_EV, -1);   /* єдине місце, де потік спить */
        if (n < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait");
            break;
        }
        for (int i = 0; i < n; i++) {
            if (evs[i].data.ptr == NULL) {
                accept_all(ep, ls);
                continue;
            }
            struct conn *c = evs[i].data.ptr;
            int dead = 0;

            if (evs[i].events & (EPOLLHUP | EPOLLERR))
                dead = 1;
            if (!dead && (evs[i].events & EPOLLOUT))
                dead = (out_flush(c) < 0);      /* спершу звільняємо місце */
            if (!dead && (evs[i].events & EPOLLIN))
                dead = (on_readable(c) < 0);
            if (!dead)
                dead = (arm(ep, c) < 0);        /* єдине місце, де міняється маска */

            if (dead)
                conn_close(ep, c);
        }
    }
    return 0;
}
