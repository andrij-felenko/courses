#include <fcntl.h>
#include <unistd.h>
#include <cerrno>
#include <cstddef>
#include <span>
#include <system_error>

// Дописати data у кінець журналу і зробити їх довговічними.
// Повертає std::error_code (0 у разі успіху).
std::error_code wal_append(int fd, std::span<const std::byte> data) {
    const char* ptr = reinterpret_cast<const char*>(data.data());
    size_t left = data.size();

    while (left > 0) {
        ssize_t n = ::write(fd, ptr, left);
        if (n < 0) {
            if (errno == EINTR) continue;
            return std::error_code(errno, std::generic_category());
        }
        ptr += static_cast<size_t>(n);
        left -= static_cast<size_t>(n);
    }

    while (::fdatasync(fd) < 0) {
        if (errno == EINTR) continue;
        return std::error_code(errno, std::generic_category());
    }
    return {};
}
