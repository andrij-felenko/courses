#include <unistd.h>
#include <system_error>
#include <expected>
#include <cerrno>

std::expected<void, std::error_code> apply_setresuid(uid_t ruid, uid_t euid, uid_t suid) noexcept {
    if (::setresuid(ruid, euid, suid) != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }
    return {};
}
