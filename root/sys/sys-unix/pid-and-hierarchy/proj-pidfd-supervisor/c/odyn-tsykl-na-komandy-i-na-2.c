enum { ST_RUN, ST_TERM, ST_KILL, ST_DONE };

/* Тіла — нижче; у файлі вони стоять перед main(). */
static void on_command(int sock, int pidfd, int *state, long *deadline);
static void on_child_exit(int ep, int *pidfd, int *state);
static void escalate(int pidfd, int *state, long *deadline);

int main(int argc, char **argv)
{
    if (argc < 3) { fprintf(stderr, "usage: sup <sock> <cmd> [args…]\n"); return 2; }
    signal(SIGPIPE, SIG_IGN);

    pid_t pid = -1;
    int pidfd = spawn(&argv[2], &pid);
    if (pidfd < 0) { perror("spawn"); return 1; }

    int sock = control_socket(argv[1]);
    if (sock < 0) { perror("control_socket"); return 1; }

    int ep = epoll_create1(EPOLL_CLOEXEC);
    struct epoll_event ev;
    ev.events = EPOLLIN;
    ev.data.fd = sock;
    epoll_ctl(ep, EPOLL_CTL_ADD, sock, &ev);
    ev.data.fd = pidfd;
    epoll_ctl(ep, EPOLL_CTL_ADD, pidfd, &ev);

    int  state = ST_RUN;
    long deadline = 0;
    fprintf(stderr, "запущено: pid=%d pidfd=%d\n", pid, pidfd);

    while (state != ST_DONE) {
        int timeout = -1;                       /* ЖИВЕ: чекаємо скільки треба */
        if (state != ST_RUN) {
            long left = deadline - now_ms();
            timeout = left > 0 ? (int)left : 0;
        }

        struct epoll_event evs[4];
        int n = epoll_wait(ep, evs, 4, timeout);
        if (n < 0) {
            if (errno == EINTR) continue;
            perror("epoll_wait");
            break;
        }
        if (n == 0) { escalate(pidfd, &state, &deadline); continue; }

        for (int i = 0; i < n; i++) {
            if (evs[i].data.fd == sock)
                on_command(sock, pidfd, &state, &deadline);
            else if (evs[i].data.fd == pidfd)
                on_child_exit(ep, &pidfd, &state);
        }
    }

    unlink(argv[1]);
    return 0;
}
