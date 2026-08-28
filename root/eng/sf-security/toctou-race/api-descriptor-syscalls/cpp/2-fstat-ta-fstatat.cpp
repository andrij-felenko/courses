#include <sys/stat.h>
#include <fcntl.h>
#include <expected>
#include <system_error>

inline std::expected<struct stat, std::error_code> get_file_stat(int fd) {
    struct stat st{};
    if (::fstat(fd, &st) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return st;
}
