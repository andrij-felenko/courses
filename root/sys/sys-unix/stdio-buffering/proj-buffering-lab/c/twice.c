/* twice.c — ./twice зламано, ./twice fix полагоджено */
#include <stdio.h>
#include <string.h>
#include <unistd.h>
#include <sys/wait.h>

int main(int argc, char **argv)
{
    int fix = (argc > 1 && strcmp(argv[1], "fix") == 0);

    printf("count: %d\n", 42);
    if (fix)
        fflush(stdout);          /* буфер порожній — копіювати нема чого */

    pid_t pid = fork();
    if (pid < 0) { perror("fork"); return 1; }
    if (pid == 0) {
        if (fix) _exit(0);       /* дитина не зливає чужого недописаного */
        return 0;                /* а так — зливає свою копію буфера */
    }
    wait(NULL);
    return 0;
}
