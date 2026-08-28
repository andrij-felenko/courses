// ============================================================================
// tele_codec.hpp — Автономний потоковий кодек пакетів телеметрії (C++20)
// ============================================================================
#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <optional>

namespace TelemetryProtocol {

inline constexpr std::uint8_t  Preamble1    = 0xAA;
inline constexpr std::uint8_t  Preamble2    = 0x55;
inline constexpr std::size_t   MaxPayload   = 64;
inline constexpr std::size_t   HeaderSize   = 5;
inline constexpr std::size_t   CrcSize      = 2;
inline constexpr std::size_t   MaxFrameSize = HeaderSize + MaxPayload + CrcSize;

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

/* Генерація таблиці CRC-16-CCITT у час компіляції (consteval) */
consteval std::array<std::uint16_t, 256> generateCrc16Lut() noexcept {
    std::array<std::uint16_t, 256> table{};
    for (std::size_t i = 0; i < 256; ++i) {
        std::uint16_t curr = static_cast<std::uint16_t>(i << 8);
        for (int b = 0; b < 8; ++b) {
            if (curr & 0x8000U) {
                curr = static_cast<std::uint16_t>((curr << 1) ^ 0x1021U);
            } else {
                curr = static_cast<std::uint16_t>(curr << 1);
            }
        }
        table[i] = curr;
    }
    return table;
}

inline constexpr auto Crc16Table = generateCrc16Lut();

inline constexpr std::uint16_t crcStep(std::uint16_t crc, std::uint8_t byte) noexcept {
    std::uint8_t idx = static_cast<std::uint8_t>((crc >> 8) ^ byte);
    return static_cast<std::uint16_t>((crc << 8) ^ Crc16Table[idx]);
}

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

    constexpr void reset() noexcept {
        m_state = State::WaitSync1;
        m_rxIndex = 0;
        m_crcAccum = 0xFFFF;
        m_crcReceived = 0;
    }

    constexpr ParserResult consumeByte(std::uint8_t byte, Packet& outPacket) noexcept {
        switch (m_state) {
        case State::WaitSync1:
            if (byte == Preamble1) {
                m_state = State::WaitSync2;
            }
            return ParserResult::NeedMoreBytes;

        case State::WaitSync2:
            if (byte == Preamble2) {
                m_state = State::GetMsgId;
                m_crcAccum = 0xFFFF;
            } else if (byte == Preamble1) {
                m_state = State::WaitSync2;
            } else {
                m_state = State::WaitSync1;
            }
            return ParserResult::NeedMoreBytes;

        case State::GetMsgId:
            m_packet.msg_id = byte;
            m_crcAccum = crcStep(m_crcAccum, byte);
            m_state = State::GetSeq;
            return ParserResult::NeedMoreBytes;

        case State::GetSeq:
            m_packet.seq = byte;
            m_crcAccum = crcStep(m_crcAccum, byte);
            m_state = State::GetLen;
            return ParserResult::NeedMoreBytes;

        case State::GetLen:
            if (byte > MaxPayload) {
                m_state = State::WaitSync1;
                return ParserResult::ErrorLength;
            }
            m_packet.len = byte;
            m_crcAccum = crcStep(m_crcAccum, byte);
            m_rxIndex = 0;
            if (m_packet.len == 0) {
                m_state = State::GetCrcLow;
            } else {
                m_state = State::GetPayload;
            }
            return ParserResult::NeedMoreBytes;

        case State::GetPayload:
            m_packet.payload[m_rxIndex++] = byte;
            m_crcAccum = crcStep(m_crcAccum, byte);
            if (m_rxIndex >= m_packet.len) {
                m_state = State::GetCrcLow;
            }
            return ParserResult::NeedMoreBytes;

        case State::GetCrcLow:
            m_crcReceived = static_cast<std::uint16_t>(byte);
            m_state = State::GetCrcHigh;
            return ParserResult::NeedMoreBytes;

        case State::GetCrcHigh:
            m_crcReceived |= static_cast<std::uint16_t>(byte << 8);
            m_state = State::WaitSync1;
            if (m_crcReceived == m_crcAccum) {
                outPacket = m_packet;
                return ParserResult::PacketReady;
            }
            return ParserResult::ErrorCrc;
        }
        m_state = State::WaitSync1;
        return ParserResult::NeedMoreBytes;
    }

private:
    State         m_state{State::WaitSync1};
    std::uint8_t  m_rxIndex{0};
    std::uint16_t m_crcAccum{0xFFFF};
    std::uint16_t m_crcReceived{0};
    Packet        m_packet{};
};

inline std::size_t serialize(std::uint8_t msgId, std::uint8_t seq,
                             std::span<const std::uint8_t> payload,
                             std::span<std::uint8_t> outBuffer) noexcept {
    if (payload.size() > MaxPayload || outBuffer.size() < (HeaderSize + payload.size() + CrcSize)) {
        return 0;
    }

    outBuffer[0] = Preamble1;
    outBuffer[1] = Preamble2;
    outBuffer[2] = msgId;
    outBuffer[3] = seq;
    outBuffer[4] = static_cast<std::uint8_t>(payload.size());

    std::uint16_t crc = 0xFFFF;
    crc = crcStep(crc, msgId);
    crc = crcStep(crc, seq);
    crc = crcStep(crc, static_cast<std::uint8_t>(payload.size()));

    for (std::size_t i = 0; i < payload.size(); ++i) {
        outBuffer[5 + i] = payload[i];
        crc = crcStep(crc, payload[i]);
    }

    outBuffer[5 + payload.size()] = static_cast<std::uint8_t>(crc & 0xFF);
    outBuffer[6 + payload.size()] = static_cast<std::uint8_t>((crc >> 8) & 0xFF);

    return HeaderSize + payload.size() + CrcSize;
}

} // namespace TelemetryProtocol
