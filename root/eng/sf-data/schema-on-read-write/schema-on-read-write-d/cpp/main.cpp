#include <iostream>
#include <string_view>
#include <charconv>
#include <optional>

namespace schema {

// 1. Schema-on-write
struct Account {
    uint32_t user_id;
    double balance;
    uint32_t created_at;
};

// 2. Schema-on-read швидкий парсер через std::string_view
std::optional<double> extract_balance(std::string_view payload) {
    constexpr std::string_view key = "\"balance\":";
    auto pos = payload.find(key);
    if (pos == std::string_view::npos) return std::nullopt;

    payload.remove_prefix(pos + key.size());
    double balance = 0.0;
    auto res = std::from_chars(payload.data(), payload.data() + payload.size(), balance);
    if (res.ec == std::errc{}) {
        return balance;
    }
    return std::nullopt;
}

} // namespace schema
