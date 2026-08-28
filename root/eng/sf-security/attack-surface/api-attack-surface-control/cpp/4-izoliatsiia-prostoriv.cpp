#include <sched.h>
#include <system_error>
#include <expected>

namespace seccomp_api {

[[nodiscard]] inline std::expected<void, std::error_code> unshare_namespaces(int flags) noexcept {
    if (::unshare(flags) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

} // namespace seccomp_api
