#include <array>
#include <span>
#include <string_view>
#include <optional>
#include <cstdint>
#include <algorithm>

struct TelemetryFrame {
    uint8_t type{0};
    std::span<const uint8_t> payload{};
    uint16_t crc{0};

    [[nodiscard]] std::string_view as_text() const noexcept {
        return std::string_view(reinterpret_cast<const char*>(payload.data()), payload.size());
    }
};

class TelemetryReceiver {
public:
    static constexpr std::size_t BUFFER_SIZE = 256;

    [[nodiscard]] std::span<uint8_t> raw_buffer() noexcept {
        return buffer_;
    }

    [[nodiscard]] std::optional<TelemetryFrame> try_parse_packet(std::size_t dma_head_pos) noexcept {
        std::size_t available = (dma_head_pos >= tail_)
            ? (dma_head_pos - tail_)
            : (BUFFER_SIZE - tail_ + dma_head_pos);

        while (available >= MIN_FRAME_SIZE) {
            uint8_t b0 = buffer_[tail_];
            uint8_t b1 = buffer_[(tail_ + 1) % BUFFER_SIZE];

            if (b0 == PREAMBLE_0 && b1 == PREAMBLE_1) {
                uint8_t msg_type = buffer_[(tail_ + 2) % BUFFER_SIZE];
                uint8_t payload_len = buffer_[(tail_ + 3) % BUFFER_SIZE];
                std::size_t total_len = 4 + payload_len + 2;

                if (available < total_len) {
                    return std::nullopt; // Очікуємо завершення прийому решти байтів через DMA
                }

                // Вирівнювання лінійного представлення для перевірки CRC
                std::array<uint8_t, 128> linear_frame{};
                for (std::size_t i = 0; i < total_len; ++i) {
                    linear_frame[i] = buffer_[(tail_ + i) % BUFFER_SIZE];
                }

                std::span<const uint8_t> frame_span(linear_frame.data(), total_len);
                std::span<const uint8_t> crc_target = frame_span.subspan(2, total_len - 4);
                uint16_t calculated = calculate_crc16(crc_target);

                uint16_t received = static_cast<uint16_t>(
                    frame_span[total_len - 2] | (frame_span[total_len - 1] << 8)
                );

                if (calculated == received) {
                    tail_ = (tail_ + total_len) % BUFFER_SIZE;
                    return TelemetryFrame{
                        .type = msg_type,
                        .payload = frame_span.subspan(4, payload_len),
                        .crc = received
                    };
                }
            }

            tail_ = (tail_ + 1) % BUFFER_SIZE;
            --available;
        }

        return std::nullopt;
    }

private:
    static constexpr uint8_t PREAMBLE_0 = 0xAA;
    static constexpr uint8_t PREAMBLE_1 = 0x55;
    static constexpr std::size_t MIN_FRAME_SIZE = 6;

    static uint16_t calculate_crc16(std::span<const uint8_t> data) noexcept {
        uint16_t crc = 0xFFFF;
        for (uint8_t b : data) {
            crc ^= static_cast<uint16_t>(b) << 8;
            for (int j = 0; j < 8; ++j) {
                crc = (crc & 0x8000) ? ((crc << 1) ^ 0x1021) : (crc << 1);
            }
        }
        return crc;
    }

    alignas(4) std::array<uint8_t, BUFFER_SIZE> buffer_{};
    std::size_t tail_{0};
};
