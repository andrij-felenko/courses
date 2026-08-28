#include <cstdint>
#include <array>
#include <cstring>
#include <span>
#include <string_view>

struct ParamExtValueMsg {
    uint16_t count{0};
    uint16_t index{0};
    std::array<char, 16> id{};
    std::array<uint8_t, 128> raw_data{};
    uint8_t type{0};

    [[nodiscard]] uint64_t as_uint64() const noexcept {
        uint64_t val = 0;
        std::memcpy(&val, raw_data.data(), sizeof(uint64_t));
        return val;
    }

    [[nodiscard]] int64_t as_int64() const noexcept {
        int64_t val = 0;
        std::memcpy(&val, raw_data.data(), sizeof(int64_t));
        return val;
    }

    [[nodiscard]] double as_double() const noexcept {
        double val = 0.0;
        std::memcpy(&val, raw_data.data(), sizeof(double));
        return val;
    }

    [[nodiscard]] std::span<const uint8_t> as_custom_blob() const noexcept {
        return std::span<const uint8_t>(raw_data.data(), raw_data.size());
    }
};
