#include <iostream>
#include <string_view>
#include <system_error>
#include <expected>
#include <unistd.h>
#include <sys/types.h>
#include <sys/prctl.h>
#include <grp.h>
#include <pwd.h>
#include <errno.h>

class PrivilegeManager {
public:
    // Безпечний виклик скидання привілеїв з поверненням std::expected
    [[nodiscard]] static std::expected<void, std::error_code> drop_permanently(std::string_view username) noexcept {
        std::string user_str(username);
        struct passwd *pw = ::getpwnam(user_str.c_str());
        if (!pw) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(errno ? errno : ENOENT)));
        }

        const uid_t target_uid = pw->pw_uid;
        const gid_t target_gid = pw->pw_gid;

        // 1. Ініціалізація додаткових груп цільового користувача
        if (::initgroups(user_str.c_str(), target_gid) != 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
        }

        // 2. Остаточне скидання GID (Real, Effective, Saved)
        if (::setresgid(target_gid, target_gid, target_gid) != 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
        }

        // 3. Остаточне скидання UID (Real, Effective, Saved)
        if (::setresuid(target_uid, target_uid, target_uid) != 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
        }

        // 4. Перевірка неможливості повернення до root
        if (::seteuid(0) != -1 || errno != EPERM) {
            return std::unexpected(std::make_error_code(std::errc::operation_not_permitted));
        }

        // 5. Захист пам'яті (заборонити coredump привілейованих даних)
        if (::prctl(PR_SET_DUMPABLE, 0, 0, 0, 0) != 0) {
            return std::unexpected(std::make_error_code(static_cast<std::errc>(errno)));
        }

        return {};
    }
};
