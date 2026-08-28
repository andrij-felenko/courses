#include <bit>
#include <cstdint>
#include <cstddef>

/* Обчислення логарифма у C++20 через бібліотеку <bit> */
[[nodiscard]] constexpr std::size_t fast_log2_cpp20(std::uint32_t x) noexcept {
    /* std::bit_width повертає кількість бітів, необхідних для представлення x.
       Для x > 0: bit_width(x) - 1 дорівнює floor(log2(x)) */
    return std::bit_width(x) - 1;
}
