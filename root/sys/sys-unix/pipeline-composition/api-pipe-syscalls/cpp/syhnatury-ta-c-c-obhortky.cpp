#include <system_error>
#include <unistd.h>
#include <fcntl.h>

void safe_dup2(int oldfd, int newfd) {
    if (::dup2(oldfd, newfd) == -1) {
        throw std::system_error(errno, std::generic_category(), "dup2 failed");
    }
}

void safe_dup3(int oldfd, int newfd, int flags = O_CLOEXEC) {
    if (::dup3(oldfd, newfd, flags) == -1) {
        throw std::system_error(errno, std::generic_category(), "dup3 failed");
    }
}
