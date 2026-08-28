static volatile sig_atomic_t death_signal_seen = 0;

static void on_parent_death(int sig)
{
    static const char msg[] = "  ← прилетів сигнал про смерть батька\n";
    ssize_t n;

    (void) sig;
    death_signal_seen = 1;
    n = write(STDOUT_FILENO, msg, sizeof msg - 1);   /* лише безпечні виклики */
    (void) n;
}

enum { PD_NORMAL, PD_RACE, PD_GUARD };

static int lab_pdeathsig(int mode)
{
    struct sigaction sa;
    pid_t parent = getpid(), kid;
    int i;

    memset(&sa, 0, sizeof sa);
    sa.sa_handler = on_parent_death;
    sigemptyset(&sa.sa_mask);
    if (sigaction(SIGTERM, &sa, NULL) == -1) {
        perror("sigaction");
        return 1;
    }

    kid = fork();
    if (kid == -1) {
        perror("fork");
        return 1;
    }

    if (kid == 0) {
        if (mode != PD_NORMAL)
            msleep(200);                     /* розчиняємо вікно навстіж */

        if (prctl(PR_SET_PDEATHSIG, (unsigned long) SIGTERM,
                  0UL, 0UL, 0UL) == -1) {
            perror("PR_SET_PDEATHSIG");
            _exit(1);
        }
        if (mode != PD_RACE && getppid() != parent) {
            printf("[робітник %d] батько зник до prctl — сигналу не буде\n",
                   (int) getpid());
            _exit(0);
        }

        for (i = 0; i < 5 && !death_signal_seen; i++) {
            printf("[робітник %d] працюю, PPID = %d\n",
                   (int) getpid(), (int) getppid());
            msleep(300);
        }
        printf("[робітник %d] кінець; сигнал %s\n", (int) getpid(),
               death_signal_seen ? "був" : "НЕ приходив");
        _exit(0);
    }

    if (mode == PD_NORMAL)
        msleep(100);                         /* даємо робітникові озброїтися */
    printf("[батько %d] виходжу\n", (int) parent);
    _exit(0);
}
