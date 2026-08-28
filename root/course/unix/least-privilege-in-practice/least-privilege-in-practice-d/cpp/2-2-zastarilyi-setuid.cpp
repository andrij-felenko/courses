#include <unistd.h>
#include <grp.h>
#include <expected>
#include <system_error>
#include <iostream>
#include <cstdlib>

// Безпечне незворотне скидання прав демона мовою C++
[[nodiscard]] std::expected<void, std::error_code> drop_privileges_permanently(uid_t target_uid, gid_t target_gid) noexcept {
    // 1. Очищення додаткових груп
    if (::setgroups(0, nullptr) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // 2. Встановлення Real, Effective, Saved GID
    if (::setresgid(target_gid, target_gid, target_gid) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // 3. Встановлення Real, Effective, Saved UID
    if (::setresuid(target_uid, target_uid, target_uid) != 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }

    // 4. Верифікація неможливості підвищення прав
    if (::setresuid(-1, 0, -1) == 0) {
        std::cerr << "КРИТИЧНА ПОМИЛКА: збережений root UID не скинуто!\n";
        std::abort();
    }

    return {};
}
