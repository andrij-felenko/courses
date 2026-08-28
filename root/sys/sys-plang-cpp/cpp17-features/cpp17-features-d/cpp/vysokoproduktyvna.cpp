#include <charconv>
#include <array>

std::array<char, 32> buffer;
double measurement = 123.456789;

// Швидке перетворення дійсного числа в рядок за алгоритмом Ryu:
auto [ptr, ec] = std::to_chars(
    buffer.data(),
    buffer.data() + buffer.size(),
    measurement,
    std::chars_format::fixed,
    3 // 3 знаки після коми
);

if (ec == std::errc()) {
    std::string_view formatted(buffer.data(), ptr - buffer.data()); // "123.457"
}
