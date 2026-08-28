#include <fcntl.h>
#include <system_error>

int get_pipe_capacity(int fd) {
    int sz = ::fcntl(fd, F_GETPIPE_SZ);
    if (sz < 0) throw std::system_error(errno, std::generic_category(), "F_GETPIPE_SZ");
    return sz;
}

int set_pipe_capacity(int fd, int new_capacity) {
    int sz = ::fcntl(fd, F_SETPIPE_SZ, new_capacity);
    if (sz < 0) throw std::system_error(errno, std::generic_category(), "F_SETPIPE_SZ");
    return sz;
}
