#pragma once

#include <array>
#include <cstddef>
#include <cstdint>
#include <optional>

namespace evse {

/*
 * Розбирач кадру зчитувача карток. Кадр: STX, вісім шістнадцяткових цифр
 * номера, дві цифри контрольної суми, ETX — саме так віддають картку поширені
 * модулі RDM6300 у 32-бітному режимі.
 *
 * Розбирач живе окремим типом без жодних зовнішніх залежностей: його можна
 * годувати байтами в модульному тесті, не піднімаючи ні черги, ні UART.
 */
class RfidFrameParser {
public:
    static constexpr std::uint8_t kStx = 0x02;
    static constexpr std::uint8_t kEtx = 0x03;
    static constexpr std::size_t  kIdDigits = 8;
    static constexpr std::size_t  kPayload  = 10; /* номер + контрольна сума */

    /* Повертає номер картки в ту мить, коли зібрався цілий справний кадр. */
    [[nodiscard]] std::optional<std::uint32_t> feed(std::uint8_t byte) noexcept
    {
        if (byte == kStx) {
            inFrame_ = true;
            length_  = 0;
            return std::nullopt;
        }

        if (!inFrame_) {
            return std::nullopt; /* сміття між кадрами */
        }

        if (byte == kEtx) {
            inFrame_ = false;
            return finish();
        }

        if (length_ < kPayload) {
            buffer_[length_++] = byte;
        } else {
            inFrame_ = false; /* кадр довший за очікуваний */
        }
        return std::nullopt;
    }

private:
    [[nodiscard]] static constexpr std::optional<std::uint8_t> hexDigit(std::uint8_t c) noexcept
    {
        if (c >= '0' && c <= '9') return static_cast<std::uint8_t>(c - '0');
        if (c >= 'A' && c <= 'F') return static_cast<std::uint8_t>(c - 'A' + 10);
        if (c >= 'a' && c <= 'f') return static_cast<std::uint8_t>(c - 'a' + 10);
        return std::nullopt;
    }

    [[nodiscard]] std::optional<std::uint32_t> finish() const noexcept
    {
        if (length_ != kPayload) {
            return std::nullopt; /* обірваний кадр */
        }

        std::uint32_t id = 0;
        for (std::size_t i = 0; i < kIdDigits; ++i) {
            const auto digit = hexDigit(buffer_[i]);
            if (!digit) {
                return std::nullopt;
            }
            id = (id << 4) | *digit;
        }

        std::uint8_t checksum = 0;
        for (std::size_t i = kIdDigits; i < kPayload; ++i) {
            const auto digit = hexDigit(buffer_[i]);
            if (!digit) {
                return std::nullopt;
            }
            checksum = static_cast<std::uint8_t>((checksum << 4) | *digit);
        }

        std::uint8_t xored = 0;
        for (unsigned shift = 0; shift < 32; shift += 8) {
            xored ^= static_cast<std::uint8_t>(id >> shift);
        }

        if (xored != checksum) {
            return std::nullopt; /* завада на лінії: кадр відкинуто */
        }
        return id;
    }

    std::array<std::uint8_t, kPayload> buffer_{};
    std::size_t                        length_{0};
    bool                               inFrame_{false};
};

} // namespace evse
