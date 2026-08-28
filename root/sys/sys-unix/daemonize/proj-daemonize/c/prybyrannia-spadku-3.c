static int reset_signals(void)
{
    struct sigaction sa;
    memset(&sa, 0, sizeof sa);
    sa.sa_handler = SIG_DFL;
    sigemptyset(&sa.sa_mask);

    for (int s = 1; s < NSIG; s++)
        (void)sigaction(s, &sa, NULL);   /* SIGKILL і SIGSTOP відмовлять — це нормально */

    sigset_t empty;
    sigemptyset(&empty);
    if (sigprocmask(SIG_SETMASK, &empty, NULL) < 0) return -1;

    sa.sa_handler = SIG_IGN;             /* обірваний співрозмовник — не привід умирати */
    if (sigaction(SIGPIPE, &sa, NULL) < 0) return -1;

    return 0;
}
