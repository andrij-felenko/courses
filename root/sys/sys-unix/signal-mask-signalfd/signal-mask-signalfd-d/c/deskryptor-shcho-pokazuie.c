sigset_t mask;
sigemptyset(&mask);
sigaddset(&mask, SIGINT);
sigaddset(&mask, SIGTERM);
sigaddset(&mask, SIGCHLD);

/* 1. без цього кроку решта не має сенсу */
pthread_sigmask(SIG_BLOCK, &mask, NULL);

/* 2. дескриптор, що бачить саме ці сигнали */
int sfd = signalfd(-1, &mask, SFD_CLOEXEC | SFD_NONBLOCK);
if (sfd < 0) { perror("signalfd"); return 1; }

/* 3. далі це звичайне джерело подій */
struct pollfd pfd = { .fd = sfd, .events = POLLIN };
for (;;) {
    if (poll(&pfd, 1, -1) < 0) { if (errno == EINTR) continue; break; }

    struct signalfd_siginfo si;
    while (read(sfd, &si, sizeof si) == (ssize_t) sizeof si) {
        if (si.ssi_signo == SIGCHLD)
            reap_children();                  /* сам сигнал зомбі не прибирає */
        else
            begin_graceful_shutdown();        /* INT або TERM */
    }
    /* read повернув EAGAIN — очікуваних більше немає, спимо далі */
}
