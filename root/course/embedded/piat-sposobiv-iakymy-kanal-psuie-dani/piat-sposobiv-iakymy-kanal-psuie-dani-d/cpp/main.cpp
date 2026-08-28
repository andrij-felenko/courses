// Ідіоматичний модульний конвеєр надійного приймача на C++20
#include <array>
#include <span>
#include <cstdint>
#include <cstddef>
#include <expected>
#include <functional>

namespace embedded::net {

enum class LinkError : std::uint8_t {
    BufferOverflow,
    CobsCorrupted,
    CrcMismatch,
    DuplicateFrame,
    FrameIncomplete
};

template <std::size_t MaxPayloadSize = 128>
class ReliableLinkReceiver {
public:
    static constexpr std::size_t HeaderSize = 1;  // 1 байт Sequence Number
    static constexpr std::size_t CrcSize = 2;     // 2 байти CRC-16
    static constexpr std::size_t MaxFrameSize = HeaderSize + MaxPayloadSize + CrcSize;
    static constexpr std::size_t CobsMaxSize = MaxFrameSize + (MaxFrameSize / 254) + 2;
    static constexpr std::uint8_t FrameDelimiter = 0x00;

    using PayloadCallback = std::function<void(std::span<const std::uint8_t>)>;
    using AckCallback = std::function<void(std::uint8_t)>;

    constexpr ReliableLinkReceiver(PayloadCallback on_payload, AckCallback on_ack) noexcept
        : on_payload_(std::move(on_payload)), on_ack_(std::move(on_ack)) {}

    // Обробка чергового байта потоку. Повертає std::expected з розміром корисних даних або кодом помилки
    [[nodiscard]] std::expected<std::size_t, LinkError> feed_byte(std::uint8_t byte) noexcept {
        if (byte == FrameDelimiter) {
            if (raw_idx_ == 0) {
                return std::unexpected(LinkError::FrameIncomplete);
            }

            auto decode_res = decode_cobs(std::span{raw_buf_.data(), raw_idx_});
            raw_idx_ = 0;

            if (!decode_res) {
                return std::unexpected(LinkError::CobsCorrupted);
            }

            const std::size_t decoded_len = *decode_res;
            if (decoded_len < (HeaderSize + CrcSize)) {
                return std::unexpected(LinkError::CrcMismatch);
            }

            // Перевірка CRC-16
            const std::uint16_t calculated_crc = compute_crc16(
                std::span{decoded_buf_.data(), decoded_len - CrcSize});
            const std::uint16_t received_crc = static_cast<std::uint16_t>(
                (decoded_buf_[decoded_len - 2] << 8) | decoded_buf_[decoded_len - 1]);

            if (calculated_crc != received_crc) {
                return std::unexpected(LinkError::CrcMismatch);
            }

            // Дедуплікація за Sequence Number
            const std::uint8_t seq = decoded_buf_[0];
            if (on_ack_) {
                on_ack_(seq); // Завжди підтверджуємо отримання
            }

            if (seq != expected_seq_) {
                return std::unexpected(LinkError::DuplicateFrame);
            }

            expected_seq_ = static_cast<std::uint8_t>(expected_seq_ + 1);

            const std::size_t payload_len = decoded_len - HeaderSize - CrcSize;
            if (on_payload_) {
                on_payload_(std::span{decoded_buf_.data() + HeaderSize, payload_len});
            }

            return payload_len;
        }

        if (raw_idx_ >= CobsMaxSize) {
            raw_idx_ = 0;
            return std::unexpected(LinkError::BufferOverflow);
        }

        raw_buf_[raw_idx_++] = byte;
        return std::unexpected(LinkError::FrameIncomplete);
    }

    constexpr void reset() noexcept {
        raw_idx_ = 0;
        expected_seq_ = 0;
    }

    [[nodiscard]] constexpr std::uint8_t expected_sequence() const noexcept {
        return expected_seq_;
    }

private:
    [[nodiscard]] static constexpr std::uint16_t compute_crc16(
        std::span<const std::uint8_t> data) noexcept {
        std::uint16_t crc = 0xFFFF;
        for (const std::uint8_t b : data) {
            crc ^= static_cast<std::uint16_t>(b) << 8;
            for (std::uint8_t bit = 0; bit < 8; ++bit) {
                if (crc & 0x8000) {
                    crc = static_cast<std::uint16_t>((crc << 1) ^ 0x1021);
                } else {
                    crc = static_cast<std::uint16_t>(crc << 1);
                }
            }
        }
        return crc;
    }

    [[nodiscard]] std::expected<std::size_t, LinkError> decode_cobs(
        std::span<const std::uint8_t> src) noexcept {
        if (src.empty()) {
            return std::unexpected(LinkError::CobsCorrupted);
        }

        std::size_t src_idx = 0;
        std::size_t dst_idx = 0;

        while (src_idx < src.size()) {
            const std::uint8_t code = src[src_idx++];
            if (code == 0) {
                return std::unexpected(LinkError::CobsCorrupted);
            }

            for (std::uint8_t i = 1; i < code; ++i) {
                if (src_idx >= src.size() || dst_idx >= decoded_buf_.size()) {
                    return std::unexpected(LinkError::CobsCorrupted);
                }
                decoded_buf_[dst_idx++] = src[src_idx++];
            }

            if (code < 0xFF && src_idx < src.size()) {
                if (dst_idx >= decoded_buf_.size()) {
                    return std::unexpected(LinkError::CobsCorrupted);
                }
                decoded_buf_[dst_idx++] = 0x00;
            }
        }

        return dst_idx;
    }

    std::array<std::uint8_t, CobsMaxSize> raw_buf_{};
    std::size_t raw_idx_{0};
    std::array<std::uint8_t, MaxFrameSize + 2> decoded_buf_{};
    std::uint8_t expected_seq_{0};
    PayloadCallback on_payload_;
    AckCallback on_ack_;
};

} // namespace embedded::net
