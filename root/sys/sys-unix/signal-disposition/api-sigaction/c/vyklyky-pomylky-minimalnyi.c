#define _POSIX_C_SOURCE 200809L
#include <signal.h>
#include <string.h>

static volatile sig_atomic_t last_sender = 0;

static void on_usr1(int signo, siginfo_t *si, void *uctx) {
    (void)signo; (void)uctx;
    last_sender = (si->si_code == SI_USER || si->si_code == SI_QUEUE)
                ? (sig_atomic_t)si->si_pid    /* si_pid значущий лише за цих кодів */
                : -1;
}

int arm_usr1(void) {
    struct sigaction sa, old;

    if (sigaction(SIGUSR1, NULL, &old) == -1)   /* act == NULL — тільки прочитати */
        return -1;
    if (old.sa_handler == SIG_IGN)              /* хтось згори вже сказав «ігнорувати» */
        return 0;                               /* — не перебиваємо його рішення      */

    memset(&sa, 0, sizeof sa);
    sa.sa_sigaction = on_usr1;                  /* НЕ sa_handler: поля в об'єднанні */
    sigemptyset(&sa.sa_mask);
    sa.sa_flags = SA_SIGINFO | SA_RESTART;

    return sigaction(SIGUSR1, &sa, NULL);       /* 0 або -1 з errno */
}
