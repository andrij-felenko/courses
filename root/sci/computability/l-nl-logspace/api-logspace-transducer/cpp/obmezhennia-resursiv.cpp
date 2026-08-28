// C++20 implementation: Memory limit configuration with std::expected
#include <sys/resource.h>
#include <system_error>
#include <expected>
#include <cstddef>
#include <cerrno>

namespace space_complexity {

[[nodiscard]] inline std::expected<void, std::error_code> set_logspace_memory_limit(size_t limit_bytes) noexcept {
    struct rlimit rl;
    rl.rlim_cur = limit_bytes;
    rl.rlim_max = limit_bytes;

    if (setrlimit(RLIMIT_AS, &rl) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

} // namespace space_complexity
