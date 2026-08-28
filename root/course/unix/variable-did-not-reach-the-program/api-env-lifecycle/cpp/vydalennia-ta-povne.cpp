#include <cstdlib>
#include <string_view>
#include <expected>
#include <system_error>

namespace sys {
[[nodiscard]] inline std::expected<void, std::error_code>
unset_env_var(std::string_view name) noexcept {
    if (::unsetenv(name.data()) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

inline void clear_all_env() noexcept {
    ::clearenv();
}
}
