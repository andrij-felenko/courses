#define _GNU_SOURCE
#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <fcntl.h>
#include <errno.h>

int create_nonblocking_custom_pipe(int fds[2], long target_size) {
    // 1. Атомарно створюємо неблокуючий канал із прапором close-on-exec
    if (pipe2(fds, O_CLOEXEC | O_NONBLOCK) == -1) {
        perror("pipe2 failed");
        return -1;
    }

    // 2. Спробуємо збільшити розмір буфера
    long actual_size = fcntl(fds[1], F_SETPIPE_SZ, target_size);
    if (actual_size == -1) {
        perror("F_SETPIPE_SZ failed (continuing with default size)");
    } else {
        printf("Pipe capacity successfully changed to %ld bytes\n", actual_size);
    }

    return 0;
}
