#include <cstdint>
#include <span>
#include <concepts>

// Шаблонне знакове розширення під час компіляції для довільної кількості бітів
template <size_t Bits, std::signed_integral TargetType = int32_t>
constexpr TargetType sign_extend(uint32_t raw) noexcept {
    static_assert(Bits < sizeof(TargetType) * 8, "Bits count must be smaller than target type width");
    constexpr uint32_t sign_bit = 1UL << (Bits - 1);
    constexpr uint32_t ext_mask = ~((1UL << Bits) - 1UL);
    
    if ((raw & sign_bit) != 0) {
        return static_cast<TargetType>(raw | ext_mask);
    }
    return static_cast<TargetType>(raw);
}

// Розпакування ліво-вирівняного 12-бітного значення через типізований інтерфейс
constexpr int16_t parse_left_aligned_12bit(std::span<const uint8_t, 2> bytes) noexcept {
    const auto raw_16 = static_cast<int16_t>((static_cast<uint16_t>(bytes[1]) << 8) |
                                              static_cast<uint16_t>(bytes[0]));
    return static_cast<int16_t>(raw_16 >> 4);
}
