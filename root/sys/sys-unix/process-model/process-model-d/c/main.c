#define _GNU_SOURCE
#include <sched.h>
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

static int shared = 0;          /* глобальна змінна батька */

static int child(void *arg)
{
    (void)arg;
    shared = 42;                /* пишемо за тією самою адресою */
    _exit(0);
}

int main(int argc, char **argv)
{
    int vm = (argc > 1 && argv[1][0] == 'v') ? CLONE_VM : 0;
    char *stack = malloc(64 * 1024);

    pid_t pid = clone(child, stack + 64 * 1024, vm | SIGCHLD, NULL);
    waitpid(pid, NULL, 0);

    printf("shared = %d\n", shared);
    free(stack);
    return 0;
}
