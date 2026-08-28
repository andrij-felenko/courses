static void on_tick(int sig) { (void) sig; }

void flood_signals(void) {                /* викликати на старті тестового прогону */
    struct sigaction sa = {0};
    sa.sa_handler = on_tick;
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = 0;                      /* без SA_RESTART — інакше нічого не видно */
    sigaction(SIGALRM, &sa, NULL);

    struct itimerval it = {
        .it_interval = { .tv_sec = 0, .tv_usec = 3000 },   /* кожні 3 мс */
        .it_value    = { .tv_sec = 0, .tv_usec = 3000 },
    };
    setitimer(ITIMER_REAL, &it, NULL);
}
