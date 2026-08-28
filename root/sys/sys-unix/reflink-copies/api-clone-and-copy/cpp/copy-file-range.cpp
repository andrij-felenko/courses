#define _GNU_SOURCE
#define _FILE_OFFSET_BITS 64
#include <unistd.h>
#include <cerrno>
#include <cstddef>
#include <system_error>

// Копіює len байтів від початку fd_in у початок fd_out за допомогою copy_file_range.
void copy_all(int fd_in, int fd_out, off_t len)
{
    off_t in_off = 0, out_off = 0;

    while (len > 0) {
        ssize_t n = ::copy_file_range(fd_in, &in_off, fd_out, &out_off,
                                       static_cast<std::size_t>(len), 0);
        if (n < 0) {
            if (errno == EINTR) continue;
            throw std::system_error(errno, std::generic_category(), "copy_file_range failed");
        }
        if (n == 0) {
            throw std::system_error(EIO, std::generic_category(), "unexpected EOF during copy_file_range");
        }
        len -= n;
    }
}
