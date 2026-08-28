#define _DEFAULT_SOURCE        /* wait4() і WCOREDUMP() */
#include <errno.h>
#include <stdio.h>
#include <sys/resource.h>
#include <sys/wait.h>
#include <unistd.h>

int main(void) {
    pid_t child = fork();
    if (child < 0) { perror("fork"); return 1; }
    if (child == 0) _exit(42);

    int status;
    struct rusage ru;
    pid_t got;
    do {
        got = wait4(child, &status, 0, &ru);
    } while (got < 0 && errno == EINTR);
    if (got < 0) { perror("wait4"); return 1; }

    if (WIFEXITED(status))
        printf("вийшов сам, код %d\n", WEXITSTATUS(status));
    else if (WIFSIGNALED(status))
        printf("убито сигналом %d%s\n", WTERMSIG(status),
               WCOREDUMP(status) ? " (дамп)" : "");

    printf("user %ld.%06ld  sys %ld.%06ld  maxrss %ld КіБ\n",
           (long)ru.ru_utime.tv_sec, (long)ru.ru_utime.tv_usec,
           (long)ru.ru_stime.tv_sec, (long)ru.ru_stime.tv_usec,
           ru.ru_maxrss);
    return 0;
}
