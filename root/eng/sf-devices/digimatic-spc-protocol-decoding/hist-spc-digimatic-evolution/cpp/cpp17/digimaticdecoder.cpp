#include <cstdint>
#include <array>
#include <optional>

class DigimaticDecoder {
public:
    enum class Unit : uint8_t { Millimeters = 0, Inches = 1 };

    struct Measurement {
        int32_t value_um;
        Unit unit;
        bool is_negative;
    };

    void reset() noexcept {
        nibbles_.fill(0);
        bit_index_ = 0;
        complete_ = false;
    }

    void on_clock_edge(bool data_bit) noexcept {
        if (complete_) return;

        const size_t nibble_idx = bit_index_ >> 2;
        const size_t bit_pos = bit_index_ & 0x03;

        if (nibble_idx < nibbles_.size()) {
            if (data_bit) {
                nibbles_[nibble_idx] |= static_cast<uint8_t>(1U << bit_pos);
            }
            ++bit_index_;
        }

        if (bit_index_ >= 52) {
            complete_ = true;
        }
    }

    [[nodiscard]] bool is_ready() const noexcept { return complete_; }

    [[nodiscard]] std::optional<Measurement> decode() const noexcept {
        if (!complete_) return std::nullopt;

        const uint16_t preamble = nibbles_[0] | (nibbles_[1] << 4) |
                                  (nibbles_[2] << 8) | (nibbles_[3] << 12);
        if (preamble != 0xFFFFU) return std::nullopt;

        int32_t mantissa = 0;
        for (size_t i = 5; i <= 10; ++i) {
            const uint8_t digit = nibbles_[i] & 0x0FU;
            if (digit > 9) return std::nullopt;
            mantissa = (mantissa * 10) + digit;
        }

        Measurement m{};
        m.is_negative = (nibbles_[4] & 0x08U) != 0;
        m.unit = (nibbles_[12] & 0x01U) ? Unit::Inches : Unit::Millimeters;

        const uint8_t decimals = nibbles_[11] & 0x07U;
        m.value_um = (m.unit == Unit::Millimeters && decimals == 2) ? (mantissa * 10) : mantissa;
        if (m.is_negative) m.value_um = -m.value_um;

        return m;
    }

private:
    std::array<uint8_t, 13> nibbles_{};
    uint8_t bit_index_{0};
    bool complete_{false};
};
