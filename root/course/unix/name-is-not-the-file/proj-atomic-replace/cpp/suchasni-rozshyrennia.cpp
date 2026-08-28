#include <filesystem>
#include <expected>
#include <system_error>
#include <fcntl.h>
#include <unistd.h>

namespace fs = std::filesystem;

[[nodiscard]] std::expected<void, std::error_code>
swap_configurations(const fs::path& active_path, const fs::path& backup_path) {
    if (::renameat2(AT_FDCWD, active_path.c_str(), AT_FDCWD, backup_path.c_str(), RENAME_EXCHANGE) < 0) {
        return std::unexpected(std::error_code(errno, std::generic_category()));
    }
    return {};
}
