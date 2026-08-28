#include <sys/sendfile.h>
#include <cstdint>
#include <cstddef>
#include <expected>
#include <system_error>

inline std::expected<size_t, std::error_code> sendSlice(
    int socketFd, int fileFd, uint64_t start, uint64_t end) noexcept
{
    off_t offset = static_cast<off_t>(start);
    size_t count = static_cast<size_t>(end - start + 1);
    ssize_t sent = ::sendfile(socketFd, fileFd, &offset, count);
    if (sent < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return static_cast<size_t>(sent);
}
