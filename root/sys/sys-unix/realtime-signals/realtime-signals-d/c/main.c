#define _POSIX_C_SOURCE 200809L
#include <signal.h>
#include <errno.h>
#include <stdio.h>

#define SIG_JOB_DONE  (SIGRTMIN + 1)   /* завдання докінчено; вантаж — його номер */
#define SIG_SHUTDOWN  (SIGRTMIN + 0)   /* менший номер = обжене чергу завершень */

int main(void)
{
    sigset_t set;
    sigemptyset(&set);
    sigaddset(&set, SIG_SHUTDOWN);
    sigaddset(&set, SIG_JOB_DONE);

    /* Блокуємо ДО того, як хтось міг надіслати: інакше типова дія вб'є процес. */
    if (sigprocmask(SIG_BLOCK, &set, NULL) == -1)   /* у потоках — pthread_sigmask */
        return 1;

    for (;;) {
        siginfo_t si;
        struct timespec wait = { .tv_sec = 5, .tv_nsec = 0 };
        int sig = sigtimedwait(&set, &si, &wait);

        if (sig == -1) {
            if (errno == EAGAIN)        /* нічого не прийшло за 5 с */
                continue;
            if (errno == EINTR)         /* урвав інший, не заблокований сигнал */
                continue;
            return 1;
        }
        if (sig == SIG_SHUTDOWN)
            break;

        /* si.si_code == SI_QUEUE, si.si_pid — хто надіслав, si_value — вантаж */
        printf("завдання %d готове (від pid %d)\n",
               si.si_value.sival_int, (int)si.si_pid);
    }
    return 0;
}
