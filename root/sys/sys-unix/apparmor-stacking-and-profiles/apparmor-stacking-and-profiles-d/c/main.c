/* c */
#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/apparmor.h>

int main(void) {
    printf("[Process %d] Current security context setup...\n", getpid());

    /* Запланувати стекування профілю 'restricted_sandbox' з існуючим профілем */
    const char *target_stack = "docker-default//&restricted_sandbox";

    if (aa_change_onexec(target_stack) < 0) {
        perror("aa_change_onexec failed");
        return EXIT_FAILURE;
    }

    printf("[Process %d] Transition scheduled. Executing worker binary...\n", getpid());

    char *args[] = { "/usr/bin/worker_bin", NULL };
    execvp(args[0], args);

    perror("execvp failed");
    return EXIT_FAILURE;
}
