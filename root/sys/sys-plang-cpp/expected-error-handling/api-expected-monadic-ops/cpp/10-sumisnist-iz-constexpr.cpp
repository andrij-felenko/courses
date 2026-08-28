constexpr std::expected<int, const char*> parse_digit(char c) {
    if (c >= '0' && c <= '9') {
        return c - '0';
    }
    return std::unexpected("Не є цифрою");
}

// Перевірка обчислення в consteval контексті
static_assert(parse_digit('5').value() == 5);
static_assert(!parse_digit('a').has_value());
static_assert(parse_digit('a').error() == std::string_view("Не є цифрою"));
