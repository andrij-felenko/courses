#include <linux/seccomp.h>
#include <linux/filter.h>
#include <sys/syscall.h>
#include <unistd.h>
#include <system_error>
#include <expected>
#include <span>

namespace seccomp_api {

enum class Operation : unsigned int {
    SetModeStrict = SECCOMP_SET_MODE_STRICT,
    SetModeFilter = SECCOMP_SET_MODE_FILTER,
    GetActionAvail = SECCOMP_GET_ACTION_AVAIL,
    GetNotifSizes = SECCOMP_GET_NOTIF_SIZES
};

[[nodiscard]] inline std::expected<int, std::error_code> invoke_seccomp(
    Operation op, unsigned int flags, void* args) noexcept {
    int res = ::syscall(SYS_seccomp, static_cast<unsigned int>(op), flags, args);
    if (res < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return res;
}

} // namespace seccomp_api
