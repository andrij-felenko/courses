#include <fcntl.h>
#include <sys/syscall.h>
#include <linux/openat2.h>
#include <unistd.h>
#include <string_view>
#include <expected>
#include <system_error>

inline std::expected<int, std::error_code> open_beneath_safe(int dirfd, std::string_view path, uint64_t flags) {
    struct open_how how{};
    how.flags = flags;
    how.resolve = RESOLVE_BENEATH | RESOLVE_NO_SYMLINKS;

    long fd = ::syscall(SYS_openat2, dirfd, path.data(), &how, sizeof(how));
    if (fd < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return static_cast<int>(fd);
}
