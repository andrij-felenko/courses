#include <cstdint>
#include <cstddef>
#include <cstring>
#include <span>
#include <optional>
#include <array>
#include <expected>

namespace embedded_protocol {

constexpr uint8_t MAGIC_BYTE = 0x5A;
constexpr size_t MAX_PAYLOAD = 128;
constexpr size_t HEADER_LEN  = 4; // Magic(1B) + Seq(1B) + Type(1B) + Len(1B)
constexpr size_t CRC_LEN     = 2;

enum class RxState {
    WaitMagic,
    ReadHeader,
    ReadPayload,
    ReadCrc
};

enum class ParseError {
    BadMagic,
    LengthOverflow,
    CrcMismatch,
    IncompleteFrame
};

struct Packet {
    uint8_t seq_num{0};
    uint8_t msg_type{0};
    uint8_t payload_len{0};
    std::array<uint8_t, MAX_PAYLOAD> payload{};
    uint16_t crc16{0};
};

class StreamReceiver {
public:
    StreamReceiver() noexcept {
        reset();
    }

    void reset() noexcept {
        state_ = RxState::WaitMagic;
        bytes_read_ = 0;
        bytes_needed_ = 0;
    }

    [[nodiscard]] constexpr static uint16_t calculate_crc16(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (const uint8_t byte : data) {
            crc ^= static_cast<uint16_t>(byte) << 8;
            for (uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x8000) {
                    crc = (crc << 1) ^ 0x1021;
                } else {
                    crc = crc << 1;
                }
            }
        }
        return crc;
    }

    std::optional<Packet> feed_byte(uint8_t byte) noexcept {
        switch (state_) {
            case RxState::WaitMagic:
                if (byte == MAGIC_BYTE) {
                    raw_buf_[0] = byte;
                    bytes_read_ = 1;
                    bytes_needed_ = HEADER_LEN;
                    state_ = RxState::ReadHeader;
                }
                break;

            case RxState::ReadHeader:
                raw_buf_[bytes_read_++] = byte;
                if (bytes_read_ == bytes_needed_) {
                    current_pkt_.seq_num = raw_buf_[1];
                    current_pkt_.msg_type = raw_buf_[2];
                    current_pkt_.payload_len = raw_buf_[3];

                    if (current_pkt_.payload_len > MAX_PAYLOAD) {
                        ++stat_len_overflows_;
                        reset();
                        break;
                    }

                    if (current_pkt_.payload_len > 0) {
                        bytes_needed_ += current_pkt_.payload_len;
                        state_ = RxState::ReadPayload;
                    } else {
                        bytes_needed_ += CRC_LEN;
                        state_ = RxState::ReadCrc;
                    }
                }
                break;

            case RxState::ReadPayload:
                raw_buf_[bytes_read_++] = byte;
                if (bytes_read_ == bytes_needed_) {
                    std::memcpy(current_pkt_.payload.data(), &raw_buf_[HEADER_LEN], current_pkt_.payload_len);
                    bytes_needed_ += CRC_LEN;
                    state_ = RxState::ReadCrc;
                }
                break;

            case RxState::ReadCrc:
                raw_buf_[bytes_read_++] = byte;
                if (bytes_read_ == bytes_needed_) {
                    const size_t crc_offset = bytes_read_ - CRC_LEN;
                    const uint16_t received_crc = static_cast<uint16_t>(raw_buf_[crc_offset]) |
                                                  (static_cast<uint16_t>(raw_buf_[crc_offset + 1]) << 8);

                    const auto crc_span = std::span<const uint8_t>(&raw_buf_[1], crc_offset - 1);
                    const uint16_t expected_crc = calculate_crc16(crc_span);

                    if (received_crc == expected_crc) {
                        current_pkt_.crc16 = received_crc;
                        ++stat_valid_frames_;
                        Packet result = current_pkt_;
                        reset();
                        return result;
                    } else {
                        ++stat_crc_errors_;
                        reset();
                    }
                }
                break;
        }

        return std::nullopt;
    }

    [[nodiscard]] uint32_t crc_errors() const noexcept { return stat_crc_errors_; }
    [[nodiscard]] uint32_t len_overflows() const noexcept { return stat_len_overflows_; }
    [[nodiscard]] uint32_t valid_frames() const noexcept { return stat_valid_frames_; }

private:
    RxState state_{RxState::WaitMagic};
    std::array<uint8_t, HEADER_LEN + MAX_PAYLOAD + CRC_LEN> raw_buf_{};
    size_t bytes_needed_{0};
    size_t bytes_read_{0};
    Packet current_pkt_{};
    uint32_t stat_crc_errors_{0};
    uint32_t stat_len_overflows_{0};
    uint32_t stat_valid_frames_{0};
};

} // namespace embedded_protocol
