#define _GNU_SOURCE
#include <unistd.h>
#include <fcntl.h>
#include <system_error>

int duplicate_with_cloexec(int src_fd, int target_fd) {
    int res = ::dup3(src_fd, target_fd, O_CLOEXEC);
    if (res == -1) {
        throw std::system_error(errno, std::generic_category(), "dup3 failed");
    }
    return res;
}
