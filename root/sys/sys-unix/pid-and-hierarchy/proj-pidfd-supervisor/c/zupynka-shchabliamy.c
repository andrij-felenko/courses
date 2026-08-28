static void on_command(int sock, int pidfd, int *state, long *deadline)
{
    char buf[64];
    ssize_t k = recv(sock, buf, sizeof buf - 1, 0);
    if (k <= 0) return;
    buf[k] = '\0';

    if (strncmp(buf, "stop", 4) == 0 && *state == ST_RUN) {
        if (sys_pidfd_kill(pidfd, SIGTERM, 0) < 0 && errno == ESRCH)
            fprintf(stderr, "уже мертва — сигнал нікуди не пішов\n");
        *state = ST_TERM;
        *deadline = now_ms() + 5000;
        fprintf(stderr, "SIGTERM надіслано, пільга 5 с\n");
    }
}

static void escalate(int pidfd, int *state, long *deadline)
{
    if (*state == ST_TERM) {
        fprintf(stderr, "пільга вичерпана — SIGKILL\n");
        sys_pidfd_kill(pidfd, SIGKILL, 0);
        *state = ST_KILL;
        *deadline = now_ms() + 2000;
    } else {
        fprintf(stderr, "SIGKILL не подіяв: дитина, найпевніше, у стані D\n");
        *deadline = now_ms() + 2000;
    }
}
