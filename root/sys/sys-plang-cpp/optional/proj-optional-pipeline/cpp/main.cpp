#include <iostream>
#include <string_view>
#include <optional>
#include <charconv>
#include <cctype>

struct ServerConfig {
    uint16_t port;
};

// Очищення пробілів у std::string_view без копіювання рядка (O(1))
constexpr std::string_view trim(std::string_view sv) noexcept {
    while (!sv.empty() && std::isspace(static_cast<unsigned char>(sv.front()))) {
        sv.remove_prefix(1);
    }
    while (!sv.empty() && std::isspace(static_cast<unsigned char>(sv.back()))) {
        sv.remove_suffix(1);
    }
    return sv;
}

// 1. Пошук ключа та витягнення значення через optional
constexpr std::optional<std::string_view> extract_value(std::string_view line, std::string_view key) noexcept {
    auto trimmed = trim(line);
    if (!trimmed.starts_with(key)) return std::nullopt;
    
    auto eq_pos = trimmed.find('=');
    if (eq_pos == std::string_view::npos) return std::nullopt;
    
    return trim(trimmed.substr(eq_pos + 1));
}

// 2. Безбезпечне перетворення рядка на число через std::from_chars
constexpr std::optional<uint32_t> parse_uint32(std::string_view sv) noexcept {
    uint32_t val = 0;
    auto [ptr, ec] = std::from_chars(sv.data(), sv.data() + sv.size(), val);
    if (ec == std::errc{} && ptr == sv.data() + sv.size()) {
        return val;
    }
    return std::nullopt;
}

// 3. Валідація діапазону порту [1..65535]
constexpr std::optional<uint16_t> validate_port(uint32_t port) noexcept {
    if (port >= 1 && port <= 65535) {
        return static_cast<uint16_t>(port);
    }
    return std::nullopt;
}

// Монадичний конвеєр C++23: об'єднання кроків у єдиний ланцюжок
constexpr std::optional<ServerConfig> parse_server_port_cpp(std::string_view config_line) noexcept {
    return extract_value(config_line, "port")
        .and_then(parse_uint32)
        .and_then(validate_port)
        .transform([](uint16_t valid_port) noexcept {
            return ServerConfig{ .port = valid_port };
        });
}
