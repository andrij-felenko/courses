#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <stdio.h>

int set_pipe_capacity(int pipe_fd, int capacity_bytes) {
    // Встановлення нового розміру кільцевого буфера ядра
    int actual_size = fcntl(pipe_fd, F_SETPIPE_SZ, capacity_bytes);
    if (actual_size == -1) {
        perror("fcntl F_SETPIPE_SZ");
        return -1;
    }
    return actual_size;
}
