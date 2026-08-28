// Ідіоматична обгортка над secure_getenv у C++
#define _GNU_SOURCE
#include <cstdlib>
#include <string_view>
#include <optional>
#include <iostream>

namespace sys {
    [[nodiscard]] std::optional<std::string_view> get_secure_env(std::string_view name) noexcept {
        const char *val = ::secure_getenv(name.data());
        if (val == nullptr) {
            return std::nullopt;
        }
        return std::string_view(val);
    }
}

void read_configuration() {
    constexpr std::string_view default_path = "/usr/lib/app/plugins";
    const auto plugin_dir = sys::get_secure_env("APP_PLUGIN_DIR").value_or(default_path);
    std::cout << "Шлях до плагінів: " << plugin_dir << '\n';
}
