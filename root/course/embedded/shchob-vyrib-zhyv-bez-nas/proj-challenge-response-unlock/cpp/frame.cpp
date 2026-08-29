#include "frame.hpp"

namespace eolboot {

std::string_view describe(FrameError error) noexcept
{
    switch (error) {
    case FrameError::CrcMismatch:    return "Frame dropped: CRC mismatch.";
    case FrameError::PayloadTooLong: return "Frame dropped: payload too long.";
    }
    return "Frame dropped: unknown decoding error.";
}

std::uint16_t crc16_update(std::uint16_t crc, std::uint8_t byte) noexcept
{
    crc ^= static_cast<std::uint16_t>(byte) << 8;
    for (int bit = 0; bit < 8; ++bit) {
        crc = (crc & 0x8000) ? static_cast<std::uint16_t>((crc << 1) ^ 0x1021)
                             : static_cast<std::uint16_t>(crc << 1);
    }
    return crc;
}

void FrameDecoder::reset() noexcept
{
    state_ = State::Sof;
    cmd_ = 0;
    len_ = 0;
    got_ = 0;
    crc_calc_ = 0xFFFF;
    crc_recv_ = 0;
}

void FrameDecoder::drop_stale(std::uint32_t now_ms) noexcept
{
    if (state_ != State::Sof && now_ms - last_byte_ms_ > FrameGapMs) {
        reset();
    }
}

std::optional<std::expected<Frame, FrameError>> FrameDecoder::push(std::uint8_t byte,
                                                                   std::uint32_t now_ms)
{
    /* Обрив передачі посеред кадру не має злипатися з наступним кадром */
    drop_stale(now_ms);
    last_byte_ms_ = now_ms;

    switch (state_) {
    case State::Sof:
        if (byte == FrameSof) {
            crc_calc_ = 0xFFFF;
            state_ = State::Cmd;
        }
        return std::nullopt;

    case State::Cmd:
        cmd_ = byte;
        crc_calc_ = crc16_update(crc_calc_, byte);
        state_ = State::LenLo;
        return std::nullopt;

    case State::LenLo:
        len_ = byte;
        crc_calc_ = crc16_update(crc_calc_, byte);
        state_ = State::LenHi;
        return std::nullopt;

    case State::LenHi:
        len_ = static_cast<std::uint16_t>(len_ | (static_cast<std::uint16_t>(byte) << 8));
        crc_calc_ = crc16_update(crc_calc_, byte);
        if (len_ > MaxPayload) {
            reset();
            return std::expected<Frame, FrameError>{ std::unexpected(FrameError::PayloadTooLong) };
        }
        got_ = 0;
        state_ = (len_ == 0) ? State::CrcLo : State::Payload;
        return std::nullopt;

    case State::Payload:
        buffer_[got_++] = byte;
        crc_calc_ = crc16_update(crc_calc_, byte);
        if (got_ == len_) {
            state_ = State::CrcLo;
        }
        return std::nullopt;

    case State::CrcLo:
        crc_recv_ = byte;
        state_ = State::CrcHi;
        return std::nullopt;

    case State::CrcHi: {
        crc_recv_ = static_cast<std::uint16_t>(crc_recv_ | (static_cast<std::uint16_t>(byte) << 8));

        const bool crc_ok = crc_recv_ == crc_calc_;
        const Frame frame{ static_cast<Cmd>(cmd_), std::span{ buffer_ }.first(len_) };

        /* Буфер лишаємо цілим: на нього дивиться payload щойно зібраного кадру */
        state_ = State::Sof;
        crc_calc_ = 0xFFFF;
        crc_recv_ = 0;
        got_ = 0;

        if (!crc_ok) {
            return std::expected<Frame, FrameError>{ std::unexpected(FrameError::CrcMismatch) };
        }
        return std::expected<Frame, FrameError>{ frame };
    }
    }

    reset();
    return std::nullopt;
}

void send_frame(Hal& hal, Cmd cmd, std::span<const std::uint8_t> payload)
{
    const auto len = static_cast<std::uint16_t>(payload.size());
    const std::array<std::uint8_t, 4> header{
        FrameSof,
        static_cast<std::uint8_t>(cmd),
        static_cast<std::uint8_t>(len & 0xFF),
        static_cast<std::uint8_t>(len >> 8),
    };

    std::uint16_t crc = 0xFFFF;
    for (const std::uint8_t b : std::span{ header }.subspan(1)) {
        crc = crc16_update(crc, b);
    }
    for (const std::uint8_t b : payload) {
        crc = crc16_update(crc, b);
    }

    const std::array<std::uint8_t, 2> tail{
        static_cast<std::uint8_t>(crc & 0xFF),
        static_cast<std::uint8_t>(crc >> 8),
    };

    hal.write(header);
    if (!payload.empty()) {
        hal.write(payload);
    }
    hal.write(tail);
}

} // namespace eolboot
