#include <iostream>
#include <filesystem>
#include <system_error>

namespace fs = std::filesystem;

fs::path get_executable_directory() {
    std::error_code ec;
    fs::path exe_path = fs::canonical("/proc/self/exe", ec);
    if (ec) {
        // Фолбек на поточний робочий каталог у разі помилки читання /proc
        return fs::current_path();
    }
    return exe_path.parent_path();
}
