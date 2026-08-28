#include <cstdint>
#include <cstring>
#include <bit>
#include <optional>

// Пакування цілого числа uint32_t через C++20 std::bit_cast
constexpr float pack_uint32_param(uint32_t val) noexcept {
    return std::bit_cast<float>(val);
}

// Безпечне типоване розпакування значення без перетворення через мантису
std::optional<uint32_t> unpack_param_to_uint32(float raw_value, uint8_t param_type) noexcept {
    if (param_type == 5 /* MAV_PARAM_TYPE_UINT32 */) {
        return std::bit_cast<uint32_t>(raw_value);
    }
    if (param_type == 1 /* MAV_PARAM_TYPE_UINT8 */) {
        uint8_t temp{};
        std::memcpy(&temp, &raw_value, sizeof(uint8_t));
        return static_cast<uint32_t>(temp);
    }
    return std::nullopt;
}
