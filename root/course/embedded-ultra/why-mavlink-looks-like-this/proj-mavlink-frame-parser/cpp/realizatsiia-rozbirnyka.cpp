#include <cstdint>
#include <array>
#include <span>
#include <optional>

namespace mavlink {

constexpr uint8_t STX_V2 = 0xFD;
constexpr size_t MAX_PAYLOAD_LEN = 255;
constexpr size_t SIGNATURE_LEN = 13;
constexpr uint8_t IFLAG_SIGNED = 0x01;

enum class ParserState : uint8_t {
    Idle,
    GotStx,
    GotLength,
    GotIncompatFlags,
    GotCompatFlags,
    GotSeq,
    GotSysId,
    GotCompId,
    GotMsgId1,
    GotMsgId2,
    GotMsgId3,
    ReceivingPayload,
    GotCrc1,
    GotCrc2,
    ReceivingSignature
};

struct Frame {
    uint8_t magic{STX_V2};
    uint8_t len{0};
    uint8_t incompat_flags{0};
    uint8_t compat_flags{0};
    uint8_t seq{0};
    uint8_t sysid{0};
    uint8_t compid{0};
    uint32_t msgid{0};
    std::array<uint8_t, MAX_PAYLOAD_LEN> payload{};
    uint16_t checksum{0};
    std::array<uint8_t, SIGNATURE_LEN> signature{};

    [[nodiscard]] std::span<const uint8_t> payload_view() const noexcept {
        return {payload.data(), len};
    }
};

class FrameParser {
public:
    constexpr FrameParser() = default;

    void reset() noexcept {
        state_ = ParserState::Idle;
        rx_count_ = 0;
        crc_accum_ = 0xFFFF;
        sig_count_ = 0;
        frame_ = Frame{};
    }

    std::optional<Frame> parse_byte(uint8_t byte, uint8_t crc_extra) noexcept {
        switch (state_) {
        case ParserState::Idle:
            if (byte == STX_V2) {
                frame_.magic = byte;
                crc_accum_ = 0xFFFF;
                state_ = ParserState::GotStx;
            }
            break;

        case ParserState::GotStx:
            frame_.len = byte;
            accumulate_crc(byte);
            state_ = ParserState::GotLength;
            break;

        case ParserState::GotLength:
            frame_.incompat_flags = byte;
            accumulate_crc(byte);
            state_ = ParserState::GotIncompatFlags;
            break;

        case ParserState::GotIncompatFlags:
            frame_.compat_flags = byte;
            accumulate_crc(byte);
            state_ = ParserState::GotCompatFlags;
            break;

        case ParserState::GotCompatFlags:
            frame_.seq = byte;
            accumulate_crc(byte);
            state_ = ParserState::GotSeq;
            break;

        case ParserState::GotSeq:
            frame_.sysid = byte;
            accumulate_crc(byte);
            state_ = ParserState::GotSysId;
            break;

        case ParserState::GotSysId:
            frame_.compid = byte;
            accumulate_crc(byte);
            state_ = ParserState::GotCompId;
            break;

        case ParserState::GotCompId:
            frame_.msgid = byte;
            accumulate_crc(byte);
            state_ = ParserState::GotMsgId1;
            break;

        case ParserState::GotMsgId1:
            frame_.msgid |= (static_cast<uint32_t>(byte) << 8);
            accumulate_crc(byte);
            state_ = ParserState::GotMsgId2;
            break;

        case ParserState::GotMsgId2:
            frame_.msgid |= (static_cast<uint32_t>(byte) << 16);
            accumulate_crc(byte);
            rx_count_ = 0;
            if (frame_.len == 0) {
                state_ = ParserState::GotCrc1;
            } else {
                state_ = ParserState::ReceivingPayload;
            }
            break;

        case ParserState::ReceivingPayload:
            frame_.payload[rx_count_++] = byte;
            accumulate_crc(byte);
            if (rx_count_ >= frame_.len) {
                state_ = ParserState::GotCrc1;
            }
            break;

        case ParserState::GotCrc1:
            frame_.checksum = byte;
            state_ = ParserState::GotCrc2;
            break;

        case ParserState::GotCrc2:
            frame_.checksum |= (static_cast<uint16_t>(byte) << 8);
            accumulate_crc(crc_extra);

            if (frame_.checksum != crc_accum_) {
                reset();
                return std::nullopt;
            }

            if (frame_.incompat_flags & IFLAG_SIGNED) {
                sig_count_ = 0;
                state_ = ParserState::ReceivingSignature;
            } else {
                Frame completed = frame_;
                reset();
                return completed;
            }
            break;

        case ParserState::ReceivingSignature:
            frame_.signature[sig_count_++] = byte;
            if (sig_count_ >= SIGNATURE_LEN) {
                Frame completed = frame_;
                reset();
                return completed;
            }
            break;
        }
        return std::nullopt;
    }

private:
    void accumulate_crc(uint8_t byte) noexcept {
        uint8_t tmp = byte ^ static_cast<uint8_t>(crc_accum_ & 0xFF);
        tmp ^= (tmp << 4);
        crc_accum_ = (crc_accum_ >> 8) ^ (static_cast<uint16_t>(tmp) << 8)
                   ^ (static_cast<uint16_t>(tmp) << 3) ^ (static_cast<uint16_t>(tmp) >> 4);
    }

    ParserState state_{ParserState::Idle};
    Frame frame_{};
    uint16_t rx_count_{0};
    uint16_t crc_accum_{0xFFFF};
    uint8_t sig_count_{0};
};

} // namespace mavlink
