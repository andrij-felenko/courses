#include <unistd.h>
#include <system_error>
#include <expected>
#include <cerrno>

std::expected<void, std::error_code> apply_seteuid(uid_t euid) noexcept {
    if (::seteuid(euid) != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }
    return {};
}
