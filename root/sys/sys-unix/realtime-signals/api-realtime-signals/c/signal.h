#define _POSIX_C_SOURCE 199309L   /* мінімум для всієї родини */
#include <signal.h>

union sigval {
    int   sival_int;
    void *sival_ptr;
};

int sigqueue(pid_t pid, int sig, const union sigval value);

int sigwaitinfo(const sigset_t *restrict set,
                siginfo_t *restrict info);
int sigtimedwait(const sigset_t *restrict set,
                 siginfo_t *restrict info,
                 const struct timespec *restrict timeout);
int sigwait(const sigset_t *restrict set, int *restrict sig);
