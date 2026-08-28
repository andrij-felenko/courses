#include <sys/prctl.h>
#include <system_error>
#include <expected>

namespace seccomp_api {

[[nodiscard]] inline std::expected<void, std::error_code> set_no_new_privs() noexcept {
    if (::prctl(PR_SET_NO_NEW_PRIVS, 1, 0, 0, 0) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

} // namespace seccomp_api
