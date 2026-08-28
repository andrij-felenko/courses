#include <pthread.h>
#include <sys/signalfd.h>

static int make_sigfd(void)
{
    sigset_t mask;

    sigemptyset(&mask);
    sigaddset(&mask, SIGTERM);
    sigaddset(&mask, SIGINT);

    /* блокувати ДО створення першого потоку: кожен новий успадкує цю маску */
    if (pthread_sigmask(SIG_BLOCK, &mask, NULL) != 0)
        return -1;

    return signalfd(-1, &mask, SFD_NONBLOCK | SFD_CLOEXEC);
}
