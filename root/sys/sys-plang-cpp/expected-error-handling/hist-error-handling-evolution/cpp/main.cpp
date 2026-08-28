// Еквівалентний C++23 підхід без errno з використанням std::expected
#include <expected>
#include <system_error>
#include <fcntl.h>

std::expected<int, std::error_code> safe_posix_open(const char* path, int flags) {
    int fd = ::open(path, flags);
    if (fd == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return fd;
}
