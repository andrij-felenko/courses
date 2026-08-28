// Обробник та валідатор пакетів STK500 v2 (C++20)
#include <cstdint>
#include <vector>
#include <span>
#include <optional>
#include <expected>

class Stk500FrameParser {
public:
    static constexpr std::uint8_t StartMarker = 0x1B;
    static constexpr std::uint8_t TokenMarker = 0x0E;
    static constexpr std::size_t MaxPayload = 300;

    struct Packet {
        std::uint8_t sequence_number{0};
        std::vector<std::uint8_t> payload;
    };

    enum class ParseError {
        InvalidHeader,
        PayloadOverflow,
        ChecksumMismatch
    };

    void reset() noexcept {
        state_ = State::Idle;
        seq_num_ = 0;
        msg_size_ = 0;
        calc_checksum_ = 0;
        payload_buffer_.clear();
    }

    [[nodiscard]] std::optional<std::expected<Packet, ParseError>> process_byte(std::uint8_t byte) {
        switch (state_) {
            case State::Idle:
                if (byte == StartMarker) {
                    calc_checksum_ = StartMarker;
                    state_ = State::SeqNum;
                }
                break;

            case State::SeqNum:
                seq_num_ = byte;
                calc_checksum_ ^= byte;
                state_ = State::SizeHigh;
                break;

            case State::SizeHigh:
                msg_size_ = static_cast<std::uint16_t>(byte << 8);
                calc_checksum_ ^= byte;
                state_ = State::SizeLow;
                break;

            case State::SizeLow:
                msg_size_ |= byte;
                calc_checksum_ ^= byte;
                if (msg_size_ == 0 || msg_size_ > MaxPayload) {
                    reset();
                    return std::unexpected(ParseError::PayloadOverflow);
                }
                payload_buffer_.reserve(msg_size_);
                state_ = State::Token;
                break;

            case State::Token:
                if (byte == TokenMarker) {
                    calc_checksum_ ^= byte;
                    state_ = State::Payload;
                } else {
                    reset();
                    return std::unexpected(ParseError::InvalidHeader);
                }
                break;

            case State::Payload:
                payload_buffer_.push_back(byte);
                calc_checksum_ ^= byte;
                if (payload_buffer_.size() >= msg_size_) {
                    state_ = State::Checksum;
                }
                break;

            case State::Checksum:
                const bool valid = (byte == calc_checksum_);
                const std::uint8_t seq = seq_num_;
                auto data = std::move(payload_buffer_);
                reset();

                if (!valid) {
                    return std::unexpected(ParseError::ChecksumMismatch);
                }
                return Packet{.sequence_number = seq, .payload = std::move(data)};
        }
        return std::nullopt; // Пакет ще не завершено
    }

private:
    enum class State {
        Idle,
        SeqNum,
        SizeHigh,
        SizeLow,
        Token,
        Payload,
        Checksum
    };

    State state_{State::Idle};
    std::uint8_t seq_num_{0};
    std::uint16_t msg_size_{0};
    std::uint8_t calc_checksum_{0};
    std::vector<std::uint8_t> payload_buffer_;
};
