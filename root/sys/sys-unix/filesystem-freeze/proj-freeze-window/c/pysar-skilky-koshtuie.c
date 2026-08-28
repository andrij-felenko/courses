static volatile sig_atomic_t stop_writer = 0;
static void on_term(int sig) { (void)sig; stop_writer = 1; }

/* Писар. Файл створено ДО заморожування: O_CREAT усередині вікна застряг би. */
static pid_t spawn_writer(const char *path)
{
    int wr = open(path, O_WRONLY | O_CREAT | O_TRUNC, 0644);
    if (wr < 0) { perror("писар: open"); return -1; }

    pid_t pid = fork();
    if (pid < 0) { perror("fork"); close(wr); return -1; }
    if (pid > 0) { close(wr); return pid; }

    struct sigaction sa = { .sa_handler = on_term };   /* без SA_RESTART */
    sigemptyset(&sa.sa_mask);
    sigaction(SIGTERM, &sa, NULL);

    char buf[4096];
    memset(buf, 'x', sizeof buf);
    double worst = 0.0;
    unsigned long long ops = 0;

    while (!stop_writer) {
        off_t off = (off_t)(ops % 256) * sizeof buf;   /* файл лишається ~1 МіБ */
        double a = now_ms();
        ssize_t n = pwrite(wr, buf, sizeof buf, off);  /* тут і буде стан D */
        double d = now_ms() - a;
        if (n < 0 && errno != EINTR) break;
        if (d > worst) worst = d;
        ops++;
        struct timespec pause = { 0, 1000000L };       /* 1 мс між записами */
        nanosleep(&pause, NULL);
    }
    fprintf(stderr, "ПИСАР: записів %llu, найдовший pwrite() = %.1f мс\n", ops, worst);
    _exit(0);
}
