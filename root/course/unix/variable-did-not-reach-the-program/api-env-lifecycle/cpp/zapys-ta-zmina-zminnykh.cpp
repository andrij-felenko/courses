#include <cstdlib>
#include <string>
#include <expected>
#include <system_error>

namespace sys {
[[nodiscard]] inline std::expected<void, std::error_code>
set_env_var(const std::string& name, const std::string& value, bool overwrite = true) noexcept {
    if (::setenv(name.c_str(), value.c_str(), overwrite ? 1 : 0) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
}
