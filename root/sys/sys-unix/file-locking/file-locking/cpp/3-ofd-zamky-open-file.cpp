#define _GNU_SOURCE
#include <fcntl.h>
#include <system_error>

void lock_ofd_range(int fd, off_t start, off_t len, short type) {
    struct flock fl{};
    fl.l_type = type;
    fl.l_whence = SEEK_SET;
    fl.l_start = start;
    fl.l_len = len;
    fl.l_pid = 0;

    while (fcntl(fd, F_OFD_SETLKW, &fl) == -1) {
        if (errno == EINTR) continue;
        throw std::system_error(errno, std::generic_category(), "F_OFD_SETLKW failed");
    }
}
