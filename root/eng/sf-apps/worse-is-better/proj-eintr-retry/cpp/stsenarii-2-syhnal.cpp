#include <unistd.h>
#include <cerrno>
#include <span>
#include <expected>
#include <system_error>

// НЕБЕЗПЕЧНИЙ КОД: втрачає дані під час часткового запису!
std::expected<std::size_t, std::error_code> broken_write_all(int fd, std::span<const char> buf) {
    ssize_t written;
    do {
        // У разі запису лише частини даних повертається частковий розмір без дозапису
        written = ::write(fd, buf.data(), buf.size());
    } while (written == -1 && errno == EINTR);

    if (written == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return static_cast<std::size_t>(written);
}
