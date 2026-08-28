#include <cstdint>
#include <cstddef>
#include <array>
#include <vector>
#include <span>
#include <optional>
#include <expected>

namespace drone::gnss {

inline constexpr uint8_t RTCM3_PREAMBLE = 0xD3;
inline constexpr size_t RTCM3_MAX_PAYLOAD = 1023;
inline constexpr size_t RTCM3_MAX_FRAME = 3 + RTCM3_MAX_PAYLOAD + 3;
inline constexpr uint32_t CRC24_QUALCOMM_POLY = 0x01864CFB;

enum class ParseError {
    NeedMoreData,
    InvalidPreamble,
    PayloadTooLarge,
    CrcMismatch,
    InvalidMessageType
};

struct Rtcm1005Data {
    uint16_t station_id{0};
    uint8_t  itrf_year{0};
    bool     has_gps{false};
    bool     has_glonass{false};
    bool     has_galileo{false};
    double   ecef_x_m{0.0};
    double   ecef_y_m{0.0};
    double   ecef_z_m{0.0};
};

class BitReader {
public:
    explicit BitReader(std::span<const uint8_t> buffer) : buffer_(buffer), bit_offset_(0) {}

    uint64_t read_bits(uint8_t num_bits) {
        uint64_t result = 0;
        for (uint8_t i = 0; i < num_bits; ++i) {
            size_t byte_idx = bit_offset_ / 8;
            uint8_t bit_idx = 7 - (bit_offset_ % 8);
            uint8_t bit_val = (buffer_[byte_idx] >> bit_idx) & 1;
            result = (result << 1) | bit_val;
            ++bit_offset_;
        }
        return result;
    }

    int64_t read_signed_bits(uint8_t num_bits) {
        uint64_t val = read_bits(num_bits);
        if (val & (1ULL << (num_bits - 1))) {
            val |= ~((1ULL << num_bits) - 1);
        }
        return static_cast<int64_t>(val);
    }

    void skip(size_t num_bits) {
        bit_offset_ += num_bits;
    }

private:
    std::span<const uint8_t> buffer_;
    size_t bit_offset_{0};
};

class RtcmParser {
public:
    static uint32_t calculate_crc24(std::span<const uint8_t> data) noexcept {
        uint32_t crc = 0x00000000;
        for (uint8_t byte : data) {
            crc ^= (static_cast<uint32_t>(byte) << 16);
            for (int j = 0; j < 8; ++j) {
                crc <<= 1;
                if (crc & 0x01000000) {
                    crc ^= CRC24_QUALCOMM_POLY;
                }
            }
        }
        return crc & 0x00FFFFFF;
    }

    std::optional<std::span<const uint8_t>> feed(uint8_t byte) {
        switch (state_) {
            case State::WaitPreamble:
                if (byte == RTCM3_PREAMBLE) {
                    buffer_[0] = byte;
                    bytes_read_ = 1;
                    state_ = State::GetHeader;
                }
                break;

            case State::GetHeader:
                buffer_[bytes_read_++] = byte;
                if (bytes_read_ == 3) {
                    payload_len_ = ((buffer_[1] & 0x03) << 8) | buffer_[2];
                    if (payload_len_ > RTCM3_MAX_PAYLOAD) {
                        state_ = State::WaitPreamble;
                    } else {
                        state_ = State::GetPayload;
                    }
                }
                break;

            case State::GetPayload:
                buffer_[bytes_read_++] = byte;
                if (bytes_read_ == 3 + payload_len_) {
                    state_ = State::GetCrc;
                }
                break;

            case State::GetCrc:
                buffer_[bytes_read_++] = byte;
                if (bytes_read_ == 3 + payload_len_ + 3) {
                    size_t crc_idx = bytes_read_ - 3;
                    uint32_t rx_crc = (static_cast<uint32_t>(buffer_[crc_idx]) << 16) |
                                      (static_cast<uint32_t>(buffer_[crc_idx + 1]) << 8) |
                                      static_cast<uint32_t>(buffer_[crc_idx + 2]);

                    uint32_t calc_crc = calculate_crc24(std::span(buffer_.data(), 3 + payload_len_));
                    state_ = State::WaitPreamble;

                    if (rx_crc == calc_crc) {
                        return std::span(buffer_.data() + 3, payload_len_);
                    }
                }
                break;
        }
        return std::nullopt;
    }

    static std::expected<Rtcm1005Data, ParseError> decode_1005(std::span<const uint8_t> payload) {
        if (payload.size() < 19) {
            return std::unexpected(ParseError::NeedMoreData);
        }

        BitReader reader(payload);
        if (reader.read_bits(12) != 1005) {
            return std::unexpected(ParseError::InvalidMessageType);
        }

        Rtcm1005Data msg;
        msg.station_id  = static_cast<uint16_t>(reader.read_bits(12));
        msg.itrf_year   = static_cast<uint8_t>(reader.read_bits(6));
        msg.has_gps     = reader.read_bits(1) != 0;
        msg.has_glonass = reader.read_bits(1) != 0;
        msg.has_galileo = reader.read_bits(1) != 0;
        reader.skip(1);

        msg.ecef_x_m = static_cast<double>(reader.read_signed_bits(38)) * 0.0001;
        reader.skip(2);
        msg.ecef_y_m = static_cast<double>(reader.read_signed_bits(38)) * 0.0001;
        reader.skip(2);
        msg.ecef_z_m = static_cast<double>(reader.read_signed_bits(38)) * 0.0001;

        return msg;
    }

private:
    enum class State { WaitPreamble, GetHeader, GetPayload, GetCrc };
    State state_{State::WaitPreamble};
    uint16_t payload_len_{0};
    size_t bytes_read_{0};
    std::array<uint8_t, RTCM3_MAX_FRAME> buffer_{};
};

} // namespace drone::gnss
