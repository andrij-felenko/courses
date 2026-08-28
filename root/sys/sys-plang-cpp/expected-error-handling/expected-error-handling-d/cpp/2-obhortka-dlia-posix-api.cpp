#include <fcntl.h>
#include <cerrno>

std::expected<int, std::error_code> posix_open(const char* path, int flags) {
    int fd = ::open(path, flags);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return fd;
}
