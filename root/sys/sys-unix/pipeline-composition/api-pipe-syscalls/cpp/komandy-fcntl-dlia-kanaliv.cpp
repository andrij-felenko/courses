#include <system_error>
#include <fcntl.h>
#include <unistd.h>

std::size_t get_cpp_pipe_capacity(int fd) {
    long sz = ::fcntl(fd, F_GETPIPE_SZ);
    if (sz == -1) {
        throw std::system_error(errno, std::generic_category(), "F_GETPIPE_SZ failed");
    }
    return static_cast<std::size_t>(sz);
}

std::size_t set_cpp_pipe_capacity(int fd, std::size_t new_size) {
    long sz = ::fcntl(fd, F_SETPIPE_SZ, static_cast<long>(new_size));
    if (sz == -1) {
        throw std::system_error(errno, std::generic_category(), "F_SETPIPE_SZ failed");
    }
    return static_cast<std::size_t>(sz);
}
