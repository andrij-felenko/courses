#include <cstdint>
#include <cstddef>
#include <span>
#include <array>

namespace crypto::constant_time {

/* Постійночасова вибірка байта з довільної таблиці пам'яті */
[[nodiscard]] uint8_t lookup_u8(std::span<const uint8_t> table, uint8_t secret_idx) noexcept {
    uint8_t result = 0;
    for (size_t i = 0; i < table.size(); ++i) {
        const auto diff = static_cast<uint8_t>(i ^ secret_idx);
        const auto mask32 = (static_cast<uint32_t>(diff) |
                             static_cast<uint32_t>(-static_cast<int32_t>(diff))) >> 31;
        uint8_t match_mask = static_cast<uint8_t>((mask32 ^ 1U) * 0xFFU);
        match_mask = barrier(match_mask);

        result |= static_cast<uint8_t>(match_mask & table[i]);
    }
    return result;
}

/* Вибірка елемента довільного типу з фіксованого масиву std::array */
template <typename T, size_t N>
[[nodiscard]] T lookup_array(const std::array<T, N> &arr, size_t secret_idx) noexcept {
    T result{};
    auto *p_res = reinterpret_cast<uint8_t*>(&result);

    for (size_t i = 0; i < N; ++i) {
        const auto diff = static_cast<uint32_t>(i ^ secret_idx);
        const auto is_match = ((diff | static_cast<uint32_t>(-static_cast<int32_t>(diff))) >> 31) ^ 1U;
        const uint8_t mask = barrier(static_cast<uint8_t>(-static_cast<int8_t>(is_match)));

        const auto *p_elem = reinterpret_cast<const uint8_t*>(&arr[i]);
        for (size_t b = 0; b < sizeof(T); ++b) {
            p_res[b] |= static_cast<uint8_t>(mask & p_elem[b]);
        }
    }
    return result;
}

} // namespace crypto::constant_time
