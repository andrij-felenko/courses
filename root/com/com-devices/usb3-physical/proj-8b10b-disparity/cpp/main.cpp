#include <cstdint>
#include <array>
#include <span>
#include <iostream>
#include <format>
#include <bitset>

enum class RunningDisparity : int8_t {
    Negative = -1,
    Positive = 1
};

enum class ControlSymbol : uint8_t {
    None,
    K28_5, // Comma / вирівнювання меж кадру (0xBC)
    K28_1, // SKP / компенсація різниці частот (0x3C)
    K28_7  // Тренувальний патерн (0xF7)
};

class Encoder8b10b {
public:
    constexpr Encoder8b10b() noexcept : rd_(RunningDisparity::Negative) {}

    // Кодування одного інформаційного байта даних
    [[nodiscard]] constexpr uint16_t encode_data(uint8_t byte) noexcept {
        return encode_internal(byte, ControlSymbol::None);
    }

    // Кодування керуючого K-символу
    [[nodiscard]] constexpr uint16_t encode_control(ControlSymbol sym) noexcept {
        return encode_internal(0x00, sym);
    }

    // Пакетне кодування буфера даних через безпечний std::span
    void encode_buffer(std::span<const uint8_t> input, std::span<uint16_t> output) noexcept {
        const size_t count = std::min(input.size(), output.size());
        for (size_t i = 0; i < count; ++i) {
            output[i] = encode_data(input[i]);
        }
    }

    [[nodiscard]] constexpr RunningDisparity current_disparity() const noexcept {
        return rd_;
    }

    constexpr void reset() noexcept {
        rd_ = RunningDisparity::Negative;
    }

private:
    RunningDisparity rd_;

    static constexpr std::array<uint8_t, 32> lut_5b6b_{
        0x27, 0x1E, 0x1D, 0x23, 0x1B, 0x25, 0x26, 0x07,
        0x17, 0x29, 0x2A, 0x0B, 0x2C, 0x0D, 0x0E, 0x38,
        0x19, 0x31, 0x32, 0x13, 0x34, 0x15, 0x16, 0x28,
        0x0C, 0x1A, 0x12, 0x39, 0x14, 0x35, 0x36, 0x2B
    };

    static constexpr std::array<uint8_t, 8> lut_3b4b_{
        0x0B, 0x09, 0x0A, 0x03, 0x07, 0x05, 0x06, 0x04
    };

    [[nodiscard]] static constexpr int popcount(uint32_t val, int bits) noexcept {
        int cnt = 0;
        for (int i = 0; i < bits; ++i) {
            if ((val >> i) & 1U) ++cnt;
        }
        return cnt;
    }

    [[nodiscard]] constexpr uint16_t encode_internal(uint8_t byte, ControlSymbol ctrl) noexcept {
        uint8_t code_6b = 0;
        uint8_t code_4b = 0;

        if (ctrl == ControlSymbol::None) {
            const uint8_t in_5b = byte & 0x1FU;
            const uint8_t in_3b = (byte >> 5U) & 0x07U;

            code_6b = lut_5b6b_[in_5b];
            code_4b = lut_3b4b_[in_3b];

            if (in_5b == 7 && rd_ == RunningDisparity::Positive) code_6b = 0x38;
            if (in_3b == 3 && rd_ == RunningDisparity::Positive) code_4b = 0x0C;
            if (in_3b == 7 && rd_ == RunningDisparity::Positive) code_4b = 0x08;
        } else if (ctrl == ControlSymbol::K28_5) {
            code_6b = (rd_ == RunningDisparity::Negative) ? 0x2FU : 0x10U;
            code_4b = (rd_ == RunningDisparity::Negative) ? 0x05U : 0x0AU;
        } else if (ctrl == ControlSymbol::K28_1) {
            code_6b = (rd_ == RunningDisparity::Negative) ? 0x2FU : 0x10U;
            code_4b = (rd_ == RunningDisparity::Negative) ? 0x09U : 0x06U;
        } else if (ctrl == ControlSymbol::K28_7) {
            code_6b = (rd_ == RunningDisparity::Negative) ? 0x2FU : 0x10U;
            code_4b = (rd_ == RunningDisparity::Negative) ? 0x07U : 0x08U;
        }

        // Обробка диспаритету 6b підблоку
        const int ones_6b = popcount(code_6b, 6);
        if (rd_ == RunningDisparity::Positive && (ones_6b != 3)) {
            code_6b = static_cast<uint8_t>((~code_6b) & 0x3FU);
        }

        const int disp_6b = popcount(code_6b, 6) - (6 - popcount(code_6b, 6));
        if (disp_6b != 0) {
            rd_ = (disp_6b > 0) ? RunningDisparity::Positive : RunningDisparity::Negative;
        }

        // Обробка диспаритету 4b підблоку
        const int ones_4b = popcount(code_4b, 4);
        if (rd_ == RunningDisparity::Positive && (ones_4b != 2)) {
            code_4b = static_cast<uint8_t>((~code_4b) & 0x0FU);
        }

        const int disp_4b = popcount(code_4b, 4) - (4 - popcount(code_4b, 4));
        if (disp_4b != 0) {
            rd_ = (disp_4b > 0) ? RunningDisparity::Positive : RunningDisparity::Negative;
        }

        return static_cast<uint16_t>((static_cast<uint16_t>(code_4b) << 6U) | (code_6b & 0x3FU));
    }
};

int main() {
    Encoder8b10b encoder;

    std::cout << "SuperSpeed USB 8b/10b C++ Encoder Testbench\n";

    // Демонстрація генерації коми K28.5 в обох станах диспаритету
    const auto k28_5_first = encoder.encode_control(ControlSymbol::K28_5);
    std::cout << std::format("K28.5 (1): 0x{:03X} [{:010b}]\n", k28_5_first, k28_5_first);

    const auto k28_5_second = encoder.encode_control(ControlSymbol::K28_5);
    std::cout << std::format("K28.5 (2): 0x{:03X} [{:010b}]\n", k28_5_second, k28_5_second);

    // Пакетне кодування тестового масиву
    const std::array<uint8_t, 4> raw_packet = {0x00, 0x55, 0xAA, 0xFF};
    std::array<uint16_t, 4> encoded_packet{};

    encoder.encode_buffer(raw_packet, encoded_packet);

    for (size_t i = 0; i < raw_packet.size(); ++i) {
        std::cout << std::format("Data 0x{:02X} -> Symbol 0x{:03X} [{:010b}]\n",
                                 raw_packet[i], encoded_packet[i], encoded_packet[i]);
    }

    return 0;
}
