#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

int resize_pipe(int pipe_fd, int target_bytes) {
    /* Отримуємо поточний розмір буфера */
    int current_sz = fcntl(pipe_fd, F_GETPIPE_SZ);
    printf("Поточний розмір буфера: %d байтів\n", current_sz);

    /* Встановлюємо новий розмір (наприклад, 1 МіБ) */
    int new_sz = fcntl(pipe_fd, F_SETPIPE_SZ, target_bytes);
    if (new_sz < 0) {
        perror("fcntl F_SETPIPE_SZ");
        return -1;
    }
    printf("Новий розмір буфера: %d байтів\n", new_sz);
    return new_sz;
}
