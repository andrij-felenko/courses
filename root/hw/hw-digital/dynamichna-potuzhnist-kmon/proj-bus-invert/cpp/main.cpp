#include <cstdint>
#include <cstddef>
#include <bit>
#include <span>
#include <array>
#include <vector>

class BusInvertChannel {
public:
    static constexpr size_t Width = 8;
    static constexpr size_t MaxTransitions = Width / 2;

    struct EncodedByte {
        uint8_t bus_data;
        bool inverted;
    };

    EncodedByte encode(uint8_t new_data) noexcept {
        const uint32_t hamming = std::popcount(static_cast<uint8_t>(new_data ^ prev_bus_data_));
        
        EncodedByte result{};
        if (hamming > MaxTransitions) {
            result.bus_data = static_cast<uint8_t>(~new_data);
            result.inverted = true;
        } else {
            result.bus_data = new_data;
            result.inverted = false;
        }

        prev_bus_data_ = result.bus_data;
        return result;
    }

    [[nodiscard]] static uint8_t decode(const EncodedByte& encoded) noexcept {
        return encoded.inverted ? static_cast<uint8_t>(~encoded.bus_data) : encoded.bus_data;
    }

private:
    uint8_t prev_bus_data_{0};
};

class BusInvert32 {
public:
    static constexpr size_t Lanes = 4;

    struct Frame {
        std::array<uint8_t, Lanes> lanes;
        uint8_t inv_flags; // 4 біти для 4 байтів
    };

    struct Stats {
        uint64_t raw_transitions{0};
        uint64_t encoded_transitions{0};

        [[nodiscard]] double power_reduction_pct() const noexcept {
            if (raw_transitions == 0) return 0.0;
            return (1.0 - static_cast<double>(encoded_transitions) / static_cast<double>(raw_transitions)) * 100.0;
        }
    };

    Frame encode_word(uint32_t word) noexcept {
        Frame frame{};
        frame.inv_flags = 0;
        uint8_t current_inv_state = 0;

        for (size_t i = 0; i < Lanes; ++i) {
            const auto byte_val = static_cast<uint8_t>((word >> (i * 8)) & 0xFF);
            
            // Враховуємо перемикання сирого сигналу для статистики
            stats_.raw_transitions += std::popcount(static_cast<uint8_t>(byte_val ^ prev_raw_bytes_[i]));
            prev_raw_bytes_[i] = byte_val;

            auto [bus_byte, is_inv] = channels_[i].encode(byte_val);
            frame.lanes[i] = bus_byte;
            
            stats_.encoded_transitions += std::popcount(static_cast<uint8_t>(bus_byte ^ prev_encoded_bytes_[i]));
            prev_encoded_bytes_[i] = bus_byte;

            if (is_inv) {
                frame.inv_flags |= static_cast<uint8_t>(1 << i);
                current_inv_state |= static_cast<uint8_t>(1 << i);
            }
        }

        // Враховуємо перемикання ліній прапорців інверсії
        stats_.encoded_transitions += std::popcount(static_cast<uint8_t>(current_inv_state ^ prev_inv_flags_));
        prev_inv_flags_ = current_inv_state;

        return frame;
    }

    [[nodiscard]] const Stats& statistics() const noexcept { return stats_; }

private:
    std::array<BusInvertChannel, Lanes> channels_{};
    std::array<uint8_t, Lanes> prev_raw_bytes_{};
    std::array<uint8_t, Lanes> prev_encoded_bytes_{};
    uint8_t prev_inv_flags_{0};
    Stats stats_{};
};
