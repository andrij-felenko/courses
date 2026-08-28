#include <unistd.h>
#include <system_error>
#include <expected>

std::expected<pid_t, std::error_code> create_isolated_session() noexcept {
    const pid_t sid = ::setsid();
    if (sid < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return sid;
}
