#include <unistd.h>
#include <cerrno>
#include <span>
#include <expected>
#include <system_error>
#include <variant>

enum class NonBlockingStatus {
    WouldBlock,
    Closed
};

std::expected<std::size_t, std::variant<NonBlockingStatus, std::error_code>> 
handle_nonblocking_read(int fd, std::span<char> buf) {
    while (true) {
        ssize_t n = ::read(fd, buf.data(), buf.size());
        if (n > 0) {
            return static_cast<std::size_t>(n);
        }
        if (n == 0) {
            return std::unexpected(NonBlockingStatus::Closed);
        }
        if (errno == EINTR) {
            continue;
        }
        if (errno == EAGAIN || errno == EWOULDBLOCK) {
            return std::unexpected(NonBlockingStatus::WouldBlock);
        }
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
}
