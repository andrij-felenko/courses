int main(void)
{
    sig_ready = SIGRTMIN + 1;

    sigset_t set;
    sigemptyset(&set);
    sigaddset(&set, sig_ready);
    sigaddset(&set, SIGIO);
    /* Блокувати в КОЖНОМУ потоці й до створення потоків: адресний сигнал
       прийде своєму потокові, а безадресний SIGIO — процесові, тобто
       будь-кому, хто його не заблокував. Типова дія SIGIO — завершити процес. */
    if (pthread_sigmask(SIG_BLOCK, &set, NULL) != 0) die("pthread_sigmask");

    listen_fd = make_listener(9000);
    arm(listen_fd);
    handle(listen_fd, POLLIN);

    const struct timespec now = { 0, 0 };          /* нульовий час — опитати чергу */

    for (;;) {
        siginfo_t si;
        if (sigwaitinfo(&set, &si) < 0) {
            if (errno == EINTR) continue;
            die("sigwaitinfo");
        }

        if (si.si_signo == sig_ready) {            /* швидкий шлях */
            ev_fast++;
            handle(si.si_fd, (int) si.si_band);
            continue;
        }

        /* SIGIO без адреси: черга не витримала, частину подій утрачено. */
        ev_rescan++;
        while (sigtimedwait(&set, &si, &now) > 0)
            ;                     /* викинути залишок черги — обхід покриє все */
        rescan();
    }
}
