#include <iostream>
#include <optional>
#include <cstdint>
#include <cassert>

// Ручна реалізація Niche-оптимізованого Optional для ненульових ідентифікаторів у C++
template <typename T, T SentinelValue = 0>
class CompactOptional {
    T value_{SentinelValue};

public:
    constexpr CompactOptional() noexcept = default;
    constexpr CompactOptional(T val) noexcept : value_(val) {
        assert(val != SentinelValue && "Значення не може дорівнювати вартовому!");
    }

    [[nodiscard]] constexpr bool has_value() const noexcept {
        return value_ != SentinelValue;
    }

    [[nodiscard]] constexpr T value() const noexcept {
        return value_;
    }
};

int main() {
    // Стандартний std::optional<uint32_t>: займає 8 байтів через паддінг тегу bool
    std::cout << "sizeof(std::optional<uint32_t>): "
              << sizeof(std::optional<uint32_t>) << " байтів\n"; // 8

    // Компактний варіант: використовує 0 як in-band вартовий, займає рівно 4 байти!
    std::cout << "sizeof(CompactOptional<uint32_t>): "
              << sizeof(CompactOptional<uint32_t>) << " байти\n"; // 4

    CompactOptional<uint32_t> opt(42);
    if (opt.has_value()) {
        std::cout << "Отримано значення: " << opt.value() << "\n";
    }

    return 0;
}
