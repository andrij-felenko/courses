#include <system_error>
#include <fcntl.h>
#include <unistd.h>

std::size_t splice_data(int fd_in, int fd_out, std::size_t len) {
    ssize_t bytes = ::splice(fd_in, nullptr, fd_out, nullptr, len, SPLICE_F_MOVE | SPLICE_F_MORE);
    if (bytes == -1) {
        throw std::system_error(errno, std::generic_category(), "splice failed");
    }
    return static_cast<std::size_t>(bytes);
}
