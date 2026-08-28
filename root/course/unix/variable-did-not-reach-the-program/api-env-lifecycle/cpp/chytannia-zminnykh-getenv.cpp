#include <cstdlib>
#include <string_view>
#include <optional>

namespace sys {
[[nodiscard]] inline std::optional<std::string_view> get_env_var(std::string_view name) noexcept {
    if (const char* val = std::getenv(name.data())) {
        return std::string_view(val);
    }
    return std::nullopt;
}
}
