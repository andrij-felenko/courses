#include <linux/landlock.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <system_error>
#include <expected>

namespace landlock_api {

[[nodiscard]] inline std::expected<int, std::error_code> create_ruleset(
    const landlock_ruleset_attr* attr, size_t size, uint32_t flags) noexcept {
    int fd = ::syscall(SYS_landlock_create_ruleset, attr, size, flags);
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return fd;
}

[[nodiscard]] inline std::expected<void, std::error_code> restrict_self(
    int ruleset_fd, uint32_t flags) noexcept {
    if (::syscall(SYS_landlock_restrict_self, ruleset_fd, flags) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

} // namespace landlock_api
