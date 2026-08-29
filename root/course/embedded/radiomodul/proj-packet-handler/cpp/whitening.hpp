#pragma once

#include <cstdint>
#include <span>

namespace radio {

// Потоковий скремблер: 7-бітний LFSR, поліном x^7 + x^4 + 1, seed 0x7F,
// період 2^7 - 1 = 127 бітів. Стан живе в об'єкті, тому один екземпляр
// проганяє весь кадр підряд. Операція самозворотна, тож той самий клас
// служить і передавачу, і приймачу — окремого «дескремблера» не буває.
class Whitener {
public:
    static constexpr std::uint8_t kSeed = 0x7F;

    void reset() noexcept { lfsr_ = kSeed; }

    [[nodiscard]] std::uint8_t operator()(std::uint8_t byte) noexcept
    {
        std::uint8_t out = 0;

        // Біти йдуть у ефір старшим першим — маска накладається так само.
        for (int bit = 7; bit >= 0; --bit) {
            const std::uint8_t maskBit = (lfsr_ >> 6) & 1u;                  // старший розряд
            const std::uint8_t feedback = ((lfsr_ >> 6) ^ (lfsr_ >> 3)) & 1u; // bit6 ^ bit3
            lfsr_ = static_cast<std::uint8_t>(((lfsr_ << 1) | feedback) & 0x7Fu);

            const std::uint8_t inBit = (byte >> bit) & 1u;
            out = static_cast<std::uint8_t>(out | ((inBit ^ maskBit) << bit));
        }
        return out;
    }

    void apply(std::span<std::uint8_t> block) noexcept
    {
        for (std::uint8_t& byte : block) {
            byte = (*this)(byte);
        }
    }

private:
    std::uint8_t lfsr_ = kSeed;
};

} // namespace radio
