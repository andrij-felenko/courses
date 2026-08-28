#include <cstdint>
#include <cstddef>
#include <span>
#include <concepts>
#include <type_traits>

namespace security {

// Безпечне порівняння двох блоків пам'яті за константний час
[[nodiscard]] bool secure_memequal(std::span<const uint8_t> a, std::span<const uint8_t> b) noexcept {
    if (a.size() != b.size()) {
        return false;
    }

    uint8_t diff = 0;
    for (size_t i = 0; i < a.size(); ++i) {
        diff |= (a[i] ^ b[i]);
    }

    // Запобігаємо оптимізаціям компілятора
    asm volatile("" : "+r"(diff) : : "memory");

    return (diff == 0);
}

// Безгалузевий вибір за допомогою бітової маски
template <std::unsigned_integral T>
[[nodiscard]] constexpr T secure_select(bool choice, T val_true, T val_false) noexcept {
    using SignedT = std::make_signed_t<T>;
    const T mask = static_cast<T>(-static_cast<SignedT>(choice ? 1 : 0));
    return (val_true & mask) | (val_false & ~mask);
}

} // namespace security
