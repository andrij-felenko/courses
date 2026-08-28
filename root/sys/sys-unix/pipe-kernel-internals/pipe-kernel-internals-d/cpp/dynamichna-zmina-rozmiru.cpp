#include <fcntl.h>
#include <unistd.h>
#include <iostream>
#include <system_error>

int resize_pipe(int pipe_fd, int target_bytes) {
    int current_sz = ::fcntl(pipe_fd, F_GETPIPE_SZ);
    if (current_sz < 0) {
        throw std::system_error(errno, std::generic_category(), "F_GETPIPE_SZ");
    }
    std::cout << "Поточний розмір буфера: " << current_sz << " байтів\n";

    int new_sz = ::fcntl(pipe_fd, F_SETPIPE_SZ, target_bytes);
    if (new_sz < 0) {
        throw std::system_error(errno, std::generic_category(), "F_SETPIPE_SZ");
    }
    std::cout << "Новий розмір буфера: " << new_sz << " байтів\n";
    return new_sz;
}
