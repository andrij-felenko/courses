#define _GNU_SOURCE
#include <unistd.h>
#include <linux/close_range.h>
#include <sys/syscall.h>
#include <system_error>

void mark_fds_close_on_exec() {
    if (::syscall(SYS_close_range, 3, ~0U, CLOSE_RANGE_CLOEXEC) == -1) {
        throw std::system_error(errno, std::generic_category(), "close_range(CLOSE_RANGE_CLOEXEC) failed");
    }
}
