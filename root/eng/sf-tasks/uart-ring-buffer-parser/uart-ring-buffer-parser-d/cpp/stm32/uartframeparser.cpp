#include <cstdint>
#include <cstddef>
#include <optional>

class UartFrameParser {
public:
    static constexpr uint8_t Preamble1 = 0xAA;
    static constexpr uint8_t Preamble2 = 0x55;
    static constexpr size_t MaxPayload = 64;

    struct Frame {
        uint8_t payload[MaxPayload];
        uint8_t length{0};
        uint8_t crc{0};
    };

    enum class State {
        Preamble1,
        Preamble2,
        ReadLength,
        ReadPayload,
        ReadCrc
    };

    UartFrameParser() = default;

    void reset() {
        state_ = State::Preamble1;
        payloadIdx_ = 0;
        calculatedCrc_ = 0;
    }

    std::optional<Frame> feedByte(uint8_t byte) {
        switch (state_) {
            case State::Preamble1:
                if (byte == Preamble1) {
                    state_ = State::Preamble2;
                }
                break;

            case State::Preamble2:
                if (byte == Preamble2) {
                    state_ = State::ReadLength;
                } else if (byte != Preamble1) {
                    state_ = State::Preamble1;
                }
                break;

            case State::ReadLength:
                if (byte > 0 && byte <= MaxPayload) {
                    currentFrame_.length = byte;
                    payloadIdx_ = 0;
                    calculatedCrc_ = byte;
                    state_ = State::ReadPayload;
                } else {
                    state_ = State::Preamble1;
                }
                break;

            case State::ReadPayload:
                currentFrame_.payload[payloadIdx_++] = byte;
                calculatedCrc_ ^= byte;
                if (payloadIdx_ >= currentFrame_.length) {
                    state_ = State::ReadCrc;
                }
                break;

            case State::ReadCrc:
                currentFrame_.crc = byte;
                if (byte == calculatedCrc_) {
                    state_ = State::Preamble1;
                    return currentFrame_;
                }
                state_ = State::Preamble1;
                break;
        }
        return std::nullopt;
    }

private:
    State state_{State::Preamble1};
    Frame currentFrame_{};
    size_t payloadIdx_{0};
    uint8_t calculatedCrc_{0};
};
