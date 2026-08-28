#include <iostream>
#include <string_view>
#include <string>
#include <optional>

namespace sys_shell {

/* Ідіоматична C++ емуляція ${var:-default} з нульовими алокаціями */
constexpr std::string_view expand_default(std::optional<std::string_view> val, 
                                          std::string_view def) noexcept {
    if (!val.has_value() || val->empty()) {
        return def;
    }
    return *val;
}

/* Емуляція ${path##*/} (basename) повертає легкий string_view зріз */
constexpr std::string_view trim_longest_prefix_slash(std::string_view path) noexcept {
    const auto pos = path.rfind('/');
    if (pos != std::string_view::npos) {
        return path.substr(pos + 1);
    }
    return path;
}

/* Емуляція ${path%/*} (dirname) */
constexpr std::string_view trim_shortest_suffix_slash(std::string_view path) noexcept {
    if (path.empty()) {
        return ".";
    }
    const auto pos = path.rfind('/');
    if (pos == std::string_view::npos) {
        return ".";
    }
    if (pos == 0) {
        return "/"; /* Корінь файлової системи */
    }
    return path.substr(0, pos);
}

} // namespace sys_shell

int main() {
    std::optional<std::string_view> env_port = std::nullopt;
    std::cout << "PORT: " << sys_shell::expand_default(env_port, "8080") << '\n';

    constexpr std::string_view file_path = "/var/log/nginx/access.log";
    std::cout << "Basename: " << sys_shell::trim_longest_prefix_slash(file_path) << '\n';
    std::cout << "Dirname:  " << sys_shell::trim_shortest_suffix_slash(file_path) << '\n';

    return 0;
}
