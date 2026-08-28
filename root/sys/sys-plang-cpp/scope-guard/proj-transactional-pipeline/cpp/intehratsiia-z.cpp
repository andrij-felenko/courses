#include <expected>
#include <string>

enum class ErrorCode { DiskFull, BadChecksum, PermissionDenied };

std::expected<void, ErrorCode> write_data_monadic(const fs::path& target) {
    const fs::path tmp = target.string() + ".tmp";
    if (!create_file(tmp)) {
        return std::unexpected(ErrorCode::PermissionDenied);
    }

    // Охоронець гарантує видалення тимчасового файлу при будь-якому ранньому return
    auto tmp_guard = make_scope_guard([&tmp] noexcept {
        std::error_code ec;
        fs::remove(tmp, ec);
    });

    auto write_res = write_payload(tmp);
    if (!write_res) {
        return std::unexpected(write_res.error()); // tmp_guard видалить файл тут!
    }

    auto check_res = verify_checksum(tmp);
    if (!check_res) {
        return std::unexpected(check_res.error()); // tmp_guard видалить файл тут!
    }

    fs::rename(tmp, target);
    tmp_guard.dismiss(); // успіх: файл залишається
    return {};
}
