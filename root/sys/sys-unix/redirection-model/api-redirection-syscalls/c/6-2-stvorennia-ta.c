#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>

int create_bound_pipe(int *read_fd, int *write_fd) {
    int pipefds[2];
    if (pipe2(pipefds, O_CLOEXEC) < 0) {
        perror("pipe2 failed");
        return -1;
    }

    *read_fd = pipefds[0];
    *write_fd = pipefds[1];
    return 0;
}
