#define SIG_READY (SIGRTMIN + 1)

static void arm(int fd)
{
    fcntl(fd, F_SETOWN, getpid());
    fcntl(fd, F_SETSIG, SIG_READY);
    int fl = fcntl(fd, F_GETFL, 0);
    fcntl(fd, F_SETFL, fl | O_ASYNC | O_NONBLOCK);
}

int main(void)
{
    sigset_t set;
    sigemptyset(&set);
    sigaddset(&set, SIG_READY);
    sigaddset(&set, SIGIO);              /* запасний шлях, див. нижче */
    sigprocmask(SIG_BLOCK, &set, NULL);  /* у багатопотоковій — pthread_sigmask */

    for (;;) {
        siginfo_t si;
        if (sigwaitinfo(&set, &si) < 0) {
            if (errno == EINTR) continue;
            die("sigwaitinfo");
        }
        if (si.si_signo == SIGIO) {      /* черга не витримала */
            rescan_everything();
            continue;
        }
        drain(si.si_fd);                 /* читаємо до EAGAIN */
    }
}
