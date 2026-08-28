#include <unistd.h>
#include <grp.h>
#include <system_error>
#include <expected>
#include <cerrno>

std::expected<void, std::error_code> clear_supplementary_groups() noexcept {
    if (::setgroups(0, nullptr) != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }
    return {};
}
