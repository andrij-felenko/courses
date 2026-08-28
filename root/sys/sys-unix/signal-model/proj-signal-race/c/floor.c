/* floor.c — намацати дно черги. gcc -O2 -Wall -o floor floor.c */
#define _GNU_SOURCE                  /* RLIMIT_SIGPENDING — розширення Linux */
#include <signal.h>
#include <stdio.h>
#include <string.h>
#include <errno.h>
#include <unistd.h>
#include <sys/resource.h>

int main(void)
{
    struct rlimit rl;
    getrlimit(RLIMIT_SIGPENDING, &rl);
    printf("успадкований м'який ліміт: %ld\n", (long) rl.rlim_cur);
    rl.rlim_cur = 16;                          /* жорсткий не чіпаємо */
    if (setrlimit(RLIMIT_SIGPENDING, &rl) != 0) { perror("setrlimit"); return 1; }

    sigset_t all;
    sigfillset(&all);
    sigprocmask(SIG_BLOCK, &all, NULL);        /* нічого не доправляється — черга росте */

    for (int i = 1; ; i++) {
        union sigval v = { .sival_int = i };
        if (sigqueue(getpid(), SIGRTMIN + 1, v) == 0) continue;
        printf("EAGAIN на %d-му записі: %s\n", i, strerror(errno));
        break;
    }
    printf("а kill(SIGUSR1) при повній черзі: %d\n", kill(getpid(), SIGUSR1));
    return 0;
}
