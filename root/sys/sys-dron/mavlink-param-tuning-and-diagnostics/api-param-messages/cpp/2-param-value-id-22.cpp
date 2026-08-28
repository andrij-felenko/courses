#include <cstdint>
#include <string_view>
#include <string>
#include <array>
#include <cstring>
#include <bit>

/* C++ структура з безпечною обробкою рядків та типізованим значенням */
struct ParamValueMsg {
    float raw_value{0.0f};
    uint16_t count{0};
    uint16_t index{0};
    std::array<char, 16> id{};
    uint8_t type{0};

    [[nodiscard]] std::string_view name() const noexcept {
        size_t len = 0;
        while (len < id.size() && id[len] != '\0') {
            ++len;
        }
        return std::string_view(id.data(), len);
    }

    [[nodiscard]] int32_t as_int32() const noexcept {
        return std::bit_cast<int32_t>(raw_value);
    }

    [[nodiscard]] uint32_t as_uint32() const noexcept {
        return std::bit_cast<uint32_t>(raw_value);
    }

    [[nodiscard]] float as_float() const noexcept {
        return raw_value;
    }
};
