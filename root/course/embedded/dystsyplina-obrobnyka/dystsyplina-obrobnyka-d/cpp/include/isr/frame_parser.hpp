// Розбір кадру — робота нижньої половини.
//
// Формат: 0x7E | довжина (1..64) | тіло | CRC-8 (поліном 0x07).
// Клас header-only й повністю constexpr-придатний, тож таблицю CRC можна
// перевірити ще на етапі збірки, а не на стенді.
#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>
#include <span>

namespace isr {

constexpr std::uint8_t crc8_update(std::uint8_t crc, std::uint8_t byte) noexcept
{
    crc ^= byte;
    for (int bit = 0; bit < 8; ++bit) {
        crc = (crc & 0x80u) ? static_cast<std::uint8_t>((crc << 1) ^ 0x07u)
                            : static_cast<std::uint8_t>(crc << 1);
    }
    return crc;
}

class FrameParser {
public:
    static constexpr std::size_t kMaxPayload = 64;
    static constexpr std::uint8_t kStartOfFrame = 0x7E;

    struct Counters {
        std::uint32_t frames_ok{0};
        std::uint32_t crc_errors{0};
        std::uint32_t length_errors{0};
    };

    // Згодовує байт. Повертає тіло кадру, щойно кадр зійшовся.
    // span дивиться у внутрішній буфер і живе до наступного виклику —
    // саме тому метод не const і повертає span, а не копію.
    std::optional<std::span<const std::uint8_t>> feed(std::uint8_t byte) noexcept
    {
        switch (state_) {
        case State::WaitStart:
            if (byte == kStartOfFrame) {
                state_ = State::WaitLength;
                crc_ = 0;
            }
            break;

        case State::WaitLength:
            if (byte == 0 || byte > kMaxPayload) {
                // Довжина поза контрактом: кадр биткий, підлаштовуватись нема під що.
                ++counters_.length_errors;
                state_ = State::WaitStart;
                break;
            }
            expected_ = byte;
            filled_ = 0;
            crc_ = crc8_update(crc_, byte);
            state_ = State::WaitBody;
            break;

        case State::WaitBody:
            payload_[filled_++] = byte;
            crc_ = crc8_update(crc_, byte);
            if (filled_ == expected_) {
                state_ = State::WaitCrc;
            }
            break;

        case State::WaitCrc:
            state_ = State::WaitStart;
            if (byte == crc_) {
                ++counters_.frames_ok;
                return std::span<const std::uint8_t>{payload_.data(), expected_};
            }
            ++counters_.crc_errors;
            break;
        }

        return std::nullopt;
    }

    [[nodiscard]] const Counters &counters() const noexcept { return counters_; }

private:
    enum class State : std::uint8_t { WaitStart, WaitLength, WaitBody, WaitCrc };

    State state_{State::WaitStart};
    std::array<std::uint8_t, kMaxPayload> payload_{};
    std::uint8_t expected_{0};
    std::uint8_t filled_{0};
    std::uint8_t crc_{0};
    Counters counters_{};
};

// Контрольне значення для кадру 7E 01 01: довжина 1, тіло 0x01, CRC 0x12.
// Помилка в поліномі чи в напрямку зсуву ловиться компілятором, а не стендом.
static_assert(crc8_update(crc8_update(0x00, 0x01), 0x01) == 0x12);

} // namespace isr
