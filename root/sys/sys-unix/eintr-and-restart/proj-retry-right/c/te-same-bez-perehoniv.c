#include <sys/signalfd.h>

int signal_channel(void) {
    sigset_t mask;
    sigemptyset(&mask);
    sigaddset(&mask, SIGTERM);
    sigaddset(&mask, SIGHUP);

    /* Блокувати ПЕРЕД створенням каналу: сигнал, що прийде між двома
       викликами, піде звичайним шляхом і таки перерве щось під рукою. */
    if (sigprocmask(SIG_BLOCK, &mask, NULL) < 0) return -1;
    return signalfd(-1, &mask, SFD_CLOEXEC | SFD_NONBLOCK);
}

static void drain_signals(int sfd) {          /* виклик із dispatch() на sfd */
    struct signalfd_siginfo si;
    while (read(sfd, &si, sizeof si) == (ssize_t) sizeof si) {
        if (si.ssi_signo == SIGTERM) want_stop = 1;
        if (si.ssi_signo == SIGHUP)  want_reload = 1;
    }
}
