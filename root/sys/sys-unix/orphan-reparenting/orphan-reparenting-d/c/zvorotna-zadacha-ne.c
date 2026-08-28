#include <sys/prctl.h>
#include <signal.h>
#include <unistd.h>

pid_t parent = getpid();
pid_t pid = fork();
if (pid == 0) {
    /* коли батько помре — надішли SIGTERM; обгортка prctl у glibc
       змінноаргументна й читає всі чотири аргументи як машинне слово */
    prctl(PR_SET_PDEATHSIG, (unsigned long) SIGTERM, 0UL, 0UL, 0UL);
    if (getppid() != parent)            /* а якщо він уже помер до цього рядка… */
        _exit(0);                       /* …сигналу не буде: виходимо самі */
    /* корисна робота дитини */
}
