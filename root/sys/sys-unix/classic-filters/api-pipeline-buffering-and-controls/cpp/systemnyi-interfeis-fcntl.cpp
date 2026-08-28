#define _GNU_SOURCE
#include <fcntl.h>
#include <unistd.h>
#include <system_error>
#include <iostream>

int set_pipe_capacity(int pipe_fd, int capacity_bytes) {
    int actual_size = fcntl(pipe_fd, F_SETPIPE_SZ, capacity_bytes);
    if (actual_size == -1) {
        throw std::system_error(errno, std::generic_category(), "fcntl F_SETPIPE_SZ failed");
    }
    return actual_size;
}
