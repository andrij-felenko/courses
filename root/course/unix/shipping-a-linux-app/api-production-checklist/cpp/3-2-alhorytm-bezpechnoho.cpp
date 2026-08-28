#include <string>
#include <string_view>
#include <filesystem>
#include <cstdlib>
#include <unistd.h>
#include <expected>
#include <system_error>

namespace fs = std::filesystem;

// Отримання шляху до конфігурації засобами std::filesystem (C++23)
[[nodiscard]] std::expected<fs::path, std::error_code> get_app_config_path(std::string_view app_name) noexcept {
    if (app_name.empty()) {
        return std::unexpected(std::make_error_code(std::errc::invalid_argument));
    }

    // Системні служби або root використовують ієрархію /etc
    if (::geteuid() == 0) {
        return fs::path("/etc") / app_name / "config.toml";
    }

    // Перевірка наявності змінної XDG_CONFIG_HOME
    const char* xdg_config = std::getenv("XDG_CONFIG_HOME");
    if (xdg_config && *xdg_config != '\0') {
        return fs::path(xdg_config) / app_name / "config.toml";
    }

    // Резервне значення $HOME/.config
    const char* home = std::getenv("HOME");
    if (!home || *home == '\0') {
        return std::unexpected(std::make_error_code(std::errc::no_such_file_or_directory));
    }

    return fs::path(home) / ".config" / app_name / "config.toml";
}
