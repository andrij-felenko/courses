#include <fcntl.h>
#include <unistd.h>
#include <expected>
#include <system_error>

std::expected<void, std::error_code> set_socket_nonblocking(int fd) {
    int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    if (::fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
