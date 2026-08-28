#include <functional>

namespace protocol {

template <size_t MaxPayload = MaxPayloadSize>
class PacketParser {
public:
    using Callback = std::function<void(const FrameHeader&, std::span<const uint8_t>)>;

    explicit PacketParser(Callback on_frame = nullptr) noexcept 
        : on_frame_(std::move(on_frame)) {}

    void feed_byte(uint8_t byte) noexcept {
        if (byte == 0x00) {
            if (state_ == State::Receive) {
                process_packet();
            }
            state_ = State::Idle;
            rx_len_ = 0;
            return;
        }

        switch (state_) {
            case State::Idle:
                rx_len_ = 0;
                rx_buf_[rx_len_++] = byte;
                state_ = State::Receive;
                break;

            case State::Receive:
                if (rx_len_ < rx_buf_.size()) {
                    rx_buf_[rx_len_++] = byte;
                } else {
                    overflow_count_++;
                    state_ = State::Overflow;
                }
                break;

            case State::Overflow:
                break;
        }
    }

    void feed_span(std::span<const uint8_t> bytes) noexcept {
        for (uint8_t b : bytes) {
            feed_byte(b);
        }
    }

    [[nodiscard]] size_t frames_received() const noexcept { return frames_count_; }
    [[nodiscard]] size_t crc_errors() const noexcept { return crc_error_count_; }
    [[nodiscard]] size_t overflow_errors() const noexcept { return overflow_count_; }

private:
    enum class State : uint8_t { Idle, Receive, Overflow };

    void process_packet() noexcept {
        if (rx_len_ < 2) return;

        auto decode_res = cobs_decode(
            std::span<const uint8_t>(rx_buf_.data(), rx_len_),
            std::span<uint8_t>(rx_buf_.data(), rx_buf_.size())
        );

        if (!decode_res) {
            crc_error_count_++;
            return;
        }

        size_t decoded_len = *decode_res;
        constexpr size_t MinLen = sizeof(FrameHeader) + sizeof(uint16_t);
        if (decoded_len < MinLen) {
            crc_error_count_++;
            return;
        }

        uint16_t calculated_crc = crc16_calculate(
            std::span<const uint8_t>(rx_buf_.data(), decoded_len - sizeof(uint16_t))
        );
        uint16_t received_crc = static_cast<uint16_t>(rx_buf_[decoded_len - 2]) |
                               (static_cast<uint16_t>(rx_buf_[decoded_len - 1]) << 8);

        if (calculated_crc != received_crc) {
            crc_error_count_++;
            return;
        }

        FrameHeader header;
        std::memcpy(&header, rx_buf_.data(), sizeof(FrameHeader));
        size_t actual_payload_len = decoded_len - sizeof(FrameHeader) - sizeof(uint16_t);

        if (header.payload_len != actual_payload_len) {
            crc_error_count_++;
            return;
        }

        frames_count_++;
        if (on_frame_) {
            on_frame_(header, std::span<const uint8_t>(
                rx_buf_.data() + sizeof(FrameHeader), actual_payload_len));
        }
    }

    State state_{State::Idle};
    std::array<uint8_t, MaxEncodedSize> rx_buf_{};
    size_t rx_len_{0};
    Callback on_frame_{nullptr};
    size_t frames_count_{0};
    size_t crc_error_count_{0};
    size_t overflow_count_{0};
};

} // namespace protocol
