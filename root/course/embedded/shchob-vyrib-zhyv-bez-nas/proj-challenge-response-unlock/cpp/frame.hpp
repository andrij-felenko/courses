#pragma once

#include <array>
#include <cstdint>
#include <expected>
#include <optional>
#include <span>
#include <string_view>

#include "hal.hpp"

namespace eolboot {

/*
 * Кадр діагностичного порту:
 *   0x55 | cmd | len_lo | len_hi | payload[len] | crc_lo | crc_hi
 * CRC-16/CCITT рахується від cmd до останнього байта payload.
 */

inline constexpr std::uint8_t FrameSof = 0x55;
inline constexpr std::size_t MaxPayload = 96;
inline constexpr std::uint32_t FrameGapMs = 1000;

enum class Cmd : std::uint8_t {
    GetChallenge  = 0x01, // хост -> пристрій
    UnlockExecute = 0x02, // хост -> пристрій, payload = підпис 64 байти
    Challenge     = 0x81, // пристрій -> хост, payload = Nonce || Chip_UUID
    Status        = 0x82, // пристрій -> хост, payload = один байт коду
};

enum class FrameError : std::uint8_t {
    CrcMismatch,
    PayloadTooLong,
};

std::string_view describe(FrameError error) noexcept;

struct Frame {
    Cmd cmd{};
    /* Дивиться в буфер декодера — дійсний до наступного push */
    std::span<const std::uint8_t> payload{};
};

class FrameDecoder {
public:
    /* nullopt — кадр іще збирається */
    [[nodiscard]] std::optional<std::expected<Frame, FrameError>> push(std::uint8_t byte,
                                                                       std::uint32_t now_ms);

    /* Кидає недозібраний кадр, якщо хост замовк посеред передачі */
    void drop_stale(std::uint32_t now_ms) noexcept;

    void reset() noexcept;

private:
    enum class State : std::uint8_t { Sof, Cmd, LenLo, LenHi, Payload, CrcLo, CrcHi };

    State state_{ State::Sof };
    std::uint8_t cmd_{};
    std::uint16_t len_{};
    std::uint16_t got_{};
    std::uint16_t crc_calc_{ 0xFFFF };
    std::uint16_t crc_recv_{};
    std::uint32_t last_byte_ms_{};
    std::array<std::uint8_t, MaxPayload> buffer_{};
};

void send_frame(Hal& hal, Cmd cmd, std::span<const std::uint8_t> payload);

[[nodiscard]] std::uint16_t crc16_update(std::uint16_t crc, std::uint8_t byte) noexcept;

} // namespace eolboot
