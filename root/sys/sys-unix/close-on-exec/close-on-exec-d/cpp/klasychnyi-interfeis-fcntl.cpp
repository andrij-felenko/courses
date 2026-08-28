#include <fcntl.h>
#include <unistd.h>
#include <system_error>

void set_cloexec(int fd) {
    const int flags = ::fcntl(fd, F_GETFD);
    if (flags == -1) {
        throw std::system_error(errno, std::generic_category(), "fcntl(F_GETFD) failed");
    }
    
    if (::fcntl(fd, F_SETFD, flags | FD_CLOEXEC) == -1) {
        throw std::system_error(errno, std::generic_category(), "fcntl(F_SETFD) failed");
    }
}
