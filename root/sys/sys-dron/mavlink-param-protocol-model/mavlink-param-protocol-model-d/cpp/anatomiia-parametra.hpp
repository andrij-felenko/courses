#include <cstdint>
#include <cstring>
#include <string_view>
#include <array>
#include <bit>

// Безпечне пакування uint32_t у float через std::bit_cast (C++20)
constexpr float pack_param_uint32(uint32_t val) noexcept {
    return std::bit_cast<float>(val);
}

// Вилучення uint32_t із контейнера float без втрати бітів
constexpr uint32_t unpack_param_uint32(float container) noexcept {
    return std::bit_cast<uint32_t>(container);
}

// Безпечне отримання string_view для 16-байтового масиву без виходу за межі
std::string_view safe_get_param_id(const std::array<char, 16>& wire_id) noexcept {
    const size_t len = strnlen(wire_id.data(), wire_id.size());
    return std::string_view(wire_id.data(), len);
}
