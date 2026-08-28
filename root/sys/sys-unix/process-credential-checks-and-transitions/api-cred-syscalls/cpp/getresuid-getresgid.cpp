#include <unistd.h>
#include <expected>
#include <system_error>
#include <cerrno>

struct UserIDs {
    uid_t ruid;
    uid_t euid;
    uid_t suid;
};

std::expected<UserIDs, std::error_code> read_all_uids() noexcept {
    UserIDs ids{};
    if (::getresuid(&ids.ruid, &ids.euid, &ids.suid) != 0) {
        return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
    }
    return ids;
}
