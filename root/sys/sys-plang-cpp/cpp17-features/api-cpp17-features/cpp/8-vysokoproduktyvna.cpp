#include <charconv>
#include <array>

std::array<char, 32> buffer;
int value = 4294967;

// Конвертація числа в рядок
auto [ptr, ec] = std::to_chars(buffer.data(), buffer.data() + buffer.size(), value);
if (ec == std::errc()) {
    std::string_view res(buffer.data(), ptr - buffer.data());
}

// Парсинг рядка в число
const char* str = "1048576";
int parsed_val = 0;
auto [parse_ptr, parse_ec] = std::from_chars(str, str + 7, parsed_val);
