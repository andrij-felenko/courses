#define _GNU_SOURCE
#include <unistd.h>
#include <linux/close_range.h>
#include <sys/syscall.h>
#include <system_error>

void close_all_inherited_fds() {
    if (::syscall(SYS_close_range, 3, ~0U, 0) == -1) {
        throw std::system_error(errno, std::generic_category(), "close_range failed");
    }
}
