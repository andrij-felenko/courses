#include <cstdint>
#include <optional>
#include <vector>
#include <span>
#include <concepts>
#include <type_traits>

namespace pairing {

/* Поняття для перевірки цілочисельних беззнакових типів */
template<typename T>
concept UnsignedIntegral = std::is_unsigned_v<T> && std::integral<T>;

/* Поняття для перевірки цілочисельних знакових типів */
template<typename T>
concept SignedIntegral = std::is_signed_v<T> && std::integral<T>;

/* Строго типізована структура для 32-бітних координат */
struct Pair32 {
    uint32_t x{0};
    uint32_t y{0};

    constexpr bool operator==(const Pair32&) const noexcept = default;
};

/* Строго типізована структура для 64-бітних координат */
struct Pair64 {
    uint64_t x{0};
    uint64_t y{0};

    constexpr bool operator==(const Pair64&) const noexcept = default;
};

/* Структура для знакових координат у просторі ℤ × ℤ */
struct SignedPair32 {
    int32_t x{0};
    int32_t y{0};

    constexpr bool operator==(const SignedPair32&) const noexcept = default;
};

} // namespace pairing
