#define _GNU_SOURCE
#include <fcntl.h>
#include <stdio.h>
#include <unistd.h>

long get_pipe_capacity(int fd) {
    // Повертає поточний розмір буфера каналу в байтах
    return fcntl(fd, F_GETPIPE_SZ);
}

long set_pipe_capacity(int fd, long new_size) {
    // Встановлює новий розмір буфера каналу (буде округлено до PAGE_SIZE)
    return fcntl(fd, F_SETPIPE_SZ, new_size);
}
