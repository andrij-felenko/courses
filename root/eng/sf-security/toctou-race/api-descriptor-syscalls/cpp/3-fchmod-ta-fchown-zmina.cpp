#include <sys/stat.h>
#include <unistd.h>
#include <expected>
#include <system_error>

inline std::expected<void, std::error_code> set_permissions_safe(int fd, mode_t mode) {
    if (::fchmod(fd, mode) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
