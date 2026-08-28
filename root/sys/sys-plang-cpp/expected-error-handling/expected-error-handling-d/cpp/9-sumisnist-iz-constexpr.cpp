constexpr std::expected<int, const char*> parse_digit(char c) {
    if (c >= '0' && c <= '9') {
        return c - '0';
    }
    return std::unexpected("Не є цифрою");
}

// Виконання парсингу та валідації під час збірки проєкту
constexpr auto result = parse_digit('7')
    .transform([](int val) { return val * 10; });

static_assert(result.has_value());
static_assert(*result == 70);
