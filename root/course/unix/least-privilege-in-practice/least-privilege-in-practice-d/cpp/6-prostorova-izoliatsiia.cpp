#include <linux/landlock.h>
#include <sys/prctl.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <system_error>
#include <expected>

// Активація обмежень Landlock мовою C++
[[nodiscard]] inline std::expected<void, std::error_code> enable_landlock_read_only() noexcept {
    landlock_ruleset_attr attr{
        .handled_access_fs = LANDLOCK_ACCESS_FS_READ_FILE | LANDLOCK_ACCESS_FS_READ_DIR,
    };
    int ruleset_fd = static_cast<int>(::syscall(__NR_landlock_create_ruleset, &attr, sizeof(attr), 0));
    if (ruleset_fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) != 0) {
        ::close(ruleset_fd);
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    if (::syscall(__NR_landlock_restrict_self, ruleset_fd, 0) != 0) {
        ::close(ruleset_fd);
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    ::close(ruleset_fd);
    return {};
}
