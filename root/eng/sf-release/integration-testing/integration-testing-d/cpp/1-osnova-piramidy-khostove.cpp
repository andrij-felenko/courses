#include <cstdint>
#include <cstddef>
#include <vector>
#include <span>
#include <optional>

class FrameParser {
public:
    static constexpr uint8_t HeaderByte = 0xAA;
    static constexpr size_t MaxPayloadSize = 64;

    enum class State {
        WaitHeader,
        ReadLength,
        ReadPayload,
        VerifyChecksum
    };

    FrameParser() { reset(); }

    void reset() noexcept {
        state_ = State::WaitHeader;
        payload_len_ = 0;
        calculated_checksum_ = 0;
        payload_buffer_.clear();
    }

    std::optional<std::vector<uint8_t>> feed_byte(uint8_t byte) {
        switch (state_) {
        case State::WaitHeader:
            if (byte == HeaderByte) {
                calculated_checksum_ = byte;
                state_ = State::ReadLength;
            }
            break;

        case State::ReadLength:
            if (byte == 0 || byte > MaxPayloadSize) {
                reset();
            } else {
                payload_len_ = byte;
                calculated_checksum_ ^= byte;
                payload_buffer_.reserve(payload_len_);
                state_ = State::ReadPayload;
            }
            break;

        case State::ReadPayload:
            payload_buffer_.push_back(byte);
            calculated_checksum_ ^= byte;
            if (payload_buffer_.size() >= payload_len_) {
                state_ = State::VerifyChecksum;
            }
            break;

        case State::VerifyChecksum: {
            bool is_valid = (byte == calculated_checksum_);
            auto result = is_valid ? std::make_optional(std::move(payload_buffer_)) : std::nullopt;
            reset();
            return result;
        }
        }
        return std::nullopt;
    }

private:
    State state_{State::WaitHeader};
    uint8_t payload_len_{0};
    uint8_t calculated_checksum_{0};
    std::vector<uint8_t> payload_buffer_{};
};
