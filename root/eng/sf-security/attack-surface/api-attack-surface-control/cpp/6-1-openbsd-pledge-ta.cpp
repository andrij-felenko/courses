#include <unistd.h>
#include <string_view>
#include <system_error>
#include <expected>

namespace openbsd_api {

[[nodiscard]] inline std::expected<void, std::error_code> apply_pledge(
    std::string_view promises, const char* execpromises = nullptr) noexcept {
    if (::pledge(promises.data(), execpromises) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

[[nodiscard]] inline std::expected<void, std::error_code> apply_unveil(
    std::string_view path, std::string_view permissions) noexcept {
    if (::unveil(path.data(), permissions.data()) == -1) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}

} // namespace openbsd_api
