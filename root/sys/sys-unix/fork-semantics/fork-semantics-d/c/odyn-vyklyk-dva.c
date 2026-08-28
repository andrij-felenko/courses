#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/wait.h>

int main(void) {
    printf("до розгалуження: pid=%d\n", getpid());

    pid_t pid = fork();
    if (pid < 0) {
        perror("fork");
        return 1;
    }
    if (pid == 0) {
        printf("дитина:  pid=%d, батько=%d\n", getpid(), getppid());
        _exit(0);
    }
    printf("батько:  pid=%d, дитина=%d\n", getpid(), pid);
    wait(NULL);
    return 0;
}
