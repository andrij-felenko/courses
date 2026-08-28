#include <unistd.h>
#include <fcntl.h>
#include <filesystem>

// Перевірка виконання засобами C++17 std::filesystem та POSIX access
bool is_executable(const std::filesystem::path& path) {
    std::error_code ec;
    auto status = std::filesystem::status(path, ec);
    if (ec || !std::filesystem::is_regular_file(status)) {
        return false;
    }
    return ::faccessat(AT_FDCWD, path.c_str(), X_OK, AT_EACCESS) == 0;
}
