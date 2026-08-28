#define _GNU_SOURCE
#include <fcntl.h>
#include <system_error>

struct flock fl{};
fl.l_type   = F_WRLCK;
fl.l_whence = SEEK_SET;
fl.l_start  = 0;
fl.l_len    = 0;
fl.l_pid    = 0;          // обов'язково 0 для OFD-замків

if (fcntl(fd, F_OFD_SETLK, &fl) == -1) {
    throw std::system_error(errno, std::generic_category(), "fcntl F_OFD_SETLK failed");
}
