// ============================================================================
// telemetry_protocol.hpp — Публічний C++-інтерфейс кодека протоколу (C++20)
// ============================================================================
#ifndef TELEMETRY_PROTOCOL_HPP
#define TELEMETRY_PROTOCOL_HPP

#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>

namespace TelemetryProtocol {

inline constexpr std::uint8_t Preamble1     = 0xAA;
inline constexpr std::uint8_t Preamble2     = 0x55;
inline constexpr std::size_t  MaxPayload    = 64;
inline constexpr std::size_t  HeaderSize    = 5;
inline constexpr std::size_t  CrcSize       = 2;
inline constexpr std::size_t  MaxFrameSize  = HeaderSize + MaxPayload + CrcSize;

enum class ParserResult : std::uint8_t {
    NeedMoreBytes,
    PacketReady,
    ErrorCrc,
    ErrorLength
};

struct Packet {
    std::uint8_t msg_id{0};
    std::uint8_t seq{0};
    std::uint8_t len{0};
    std::array<std::uint8_t, MaxPayload> payload{};
};

class StreamParser {
public:
    enum class State : std::uint8_t {
        WaitSync1,
        WaitSync2,
        GetMsgId,
        GetSeq,
        GetLen,
        GetPayload,
        GetCrcLow,
        GetCrcHigh
    };

    constexpr StreamParser() noexcept = default;
    void reset() noexcept;
    ParserResult consumeByte(std::uint8_t byte, Packet& outPacket) noexcept;

private:
    State         m_state{State::WaitSync1};
    std::uint8_t  m_rxIndex{0};
    std::uint16_t m_runningCrc{0xFFFF};
    std::uint16_t m_receivedCrc{0};
    Packet        m_packet{};
};

std::size_t serialize(std::uint8_t msgId, std::uint8_t seq,
                      std::span<const std::uint8_t> payload,
                      std::span<std::uint8_t> outBuffer) noexcept;

} // namespace TelemetryProtocol

#endif // TELEMETRY_PROTOCOL_HPP
