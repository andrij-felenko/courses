#include <optional>

std::optional<int> parse_port(std::string_view str) {
    if (str.empty()) return std::nullopt;
    int port = std::atoi(str.data());
    if (port <= 0 || port > 65535) return std::nullopt;
    return port;
}

auto port = parse_port("8080");
// Безпечне отримання значення зі значенням за замовчуванням:
int active_port = port.value_or(80);
