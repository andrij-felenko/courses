#include <errno.h>
#include <unistd.h>

#include <expected>
#include <span>
#include <system_error>

std::expected<void, std::error_code> drain_master_fd(int master_fd, std::span<char> buffer) {
    while (true) {
        ssize_t n = ::read(master_fd, buffer.data(), buffer.size());
        if (n < 0) {
            if (errno == EIO) {
                /* Нормальне завершення: підлеглий кінець закрито */
                return {};
            }
            if (errno == EINTR) {
                continue;
            }
            return std::unexpected(std::error_code(errno, std::generic_category()));
        }
        if (n == 0) {
            return {};
        }
        ::write(STDOUT_FILENO, buffer.data(), static_cast<size_t>(n));
    }
}
