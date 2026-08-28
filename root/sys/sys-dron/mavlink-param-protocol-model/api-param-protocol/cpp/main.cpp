#include <cstdint>
#include <cstring>
#include <string>
#include <string_view>
#include <array>
#include <variant>
#include <bit>

// Типобезпечне представлення значення параметра в C++20
using ParamValueVariant = std::variant<
    uint8_t, int8_t, uint16_t, int16_t, uint32_t, int32_t, float
>;

// Безпечне перетворення сирого масиву param_id у string_view
std::string_view extract_param_id_view(const std::array<char, 16>& wire_id) noexcept {
    const size_t len = strnlen(wire_id.data(), 16);
    return std::string_view(wire_id.data(), len);
}

// Упаковка варіанта у 32-бітний float-контейнер через bit_cast
float pack_param_variant(const ParamValueVariant& val) noexcept {
    return std::visit([](auto&& arg) -> float {
        using T = std::decay_t<decltype(arg)>;
        if constexpr (std::is_same_v<T, float>) {
            return arg;
        } else if constexpr (sizeof(T) == 4) {
            return std::bit_cast<float>(arg);
        } else if constexpr (sizeof(T) < 4) {
            uint32_t container = 0;
            if constexpr (std::is_signed_v<T>) {
                const auto extended = static_cast<int32_t>(arg);
                container = std::bit_cast<uint32_t>(extended);
            } else {
                container = static_cast<uint32_t>(arg);
            }
            return std::bit_cast<float>(container);
        } else {
            return 0.0f;
        }
    }, val);
}
