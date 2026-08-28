#include <cstdint>
#include <bit>
#include <concepts>

/* Сучасна ідіоматична C++20 реалізація через std::bit_cast (constexpr та zero-cost) */

template <std::integral T>
[[nodiscard]] constexpr float pack_integral_to_mavlink_float(T val) noexcept {
    static_assert(sizeof(T) <= sizeof(float), "Тип перевищує 32 біти контейнера");
    if constexpr (sizeof(T) == sizeof(float)) {
        return std::bit_cast<float>(val);
    } else {
        /* Для типів < 4 байтів вирівнюємо в uint32_t перед копіюванням */
        uint32_t wider = static_cast<uint32_t>(val);
        return std::bit_cast<float>(wider);
    }
}

template <std::integral T>
[[nodiscard]] constexpr T unpack_mavlink_float_to_integral(float f) noexcept {
    static_assert(sizeof(T) <= sizeof(float), "Тип перевищує 32 біти контейнера");
    if constexpr (sizeof(T) == sizeof(float)) {
        return std::bit_cast<T>(f);
    } else {
        uint32_t wider = std::bit_cast<uint32_t>(f);
        return static_cast<T>(wider);
    }
}
