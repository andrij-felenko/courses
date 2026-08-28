// Налаштування неблокувального режиму дескриптора в C++
#include <fcntl.h>
#include <system_error>

std::error_code set_nonblocking(int fd) noexcept {
    const int flags = ::fcntl(fd, F_GETFL, 0);
    if (flags < 0) {
        return std::error_code(errno, std::generic_category());
    }
    if (::fcntl(fd, F_SETFL, flags | O_NONBLOCK) < 0) {
        return std::error_code(errno, std::generic_category());
    }
    return {};
}
