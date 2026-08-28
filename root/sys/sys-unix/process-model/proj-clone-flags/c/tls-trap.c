/* tls-trap.c — у ручного клона немає власної пам'яті потоку */
#define _GNU_SOURCE
#include <errno.h>
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

static int spoil(void *arg)
{
    (void)arg;
    close(-1);            /* завідомо провал: ядро віддасть EBADF */
    return 0;
}

int main(void)
{
    char *stack = malloc(64 * 1024);
    pid_t t;
    int e;

    errno = 0;
    t = clone(spoil, stack + 64 * 1024, CLONE_VM | SIGCHLD, NULL);
    waitpid(t, NULL, 0);
    e = errno;
    printf("errno у батька: %d (%s)\n", e, strerror(e));
    return 0;
}
