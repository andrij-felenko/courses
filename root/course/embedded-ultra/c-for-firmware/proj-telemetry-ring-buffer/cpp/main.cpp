#include <cstdint>
#include <cstddef>
#include <array>
#include <optional>
#include <span>
#include <cstring>

inline constexpr uint8_t FRAME_START_BYTE = 0xAA;
inline constexpr uint8_t FRAME_END_BYTE   = 0x55;

// --- C++20 упакована структура корисного навантаження ---
struct [[gnu::packed]] TelemetryPayload {
    uint8_t  node_id;
    uint32_t timestamp_ms;
    int16_t  accel_x;
    int16_t  accel_y;
    int16_t  accel_z;
    uint16_t voltage_mv;
    uint16_t sequence_id;
};

inline constexpr size_t PAYLOAD_SIZE = sizeof(TelemetryPayload);
static_assert(PAYLOAD_SIZE == 15, "Payload size must be exactly 15 bytes!");

// --- Шаблонний безпечний буфер SPSC ---
template <typename T, size_t Capacity>
class StaticRingBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be power of two");
public:
    constexpr StaticRingBuffer() noexcept = default;

    bool push(T item) noexcept {
        size_t next = (head_ + 1U) & mask_;
        if (next == tail_) return false;
        buffer_[head_] = item;
        head_ = next;
        return true;
    }

    std::optional<T> pop() noexcept {
        if (head_ == tail_) return std::nullopt;
        T item = buffer_[tail_];
        tail_ = (tail_ + 1U) & mask_;
        return item;
    }

private:
    static constexpr size_type mask_ = Capacity - 1U;
    std::array<T, Capacity> buffer_{};
    volatile size_t head_{0};
    volatile size_t tail_{0};
};

// --- Обчислення CRC16-CCITT на std::span ---
constexpr uint16_t calculate_crc16(std::span<const uint8_t> data) noexcept {
    uint16_t crc = 0xFFFFU;
    for (uint8_t b : data) {
        crc ^= static_cast<uint16_t>(static_cast<uint16_t>(b) << 8);
        for (uint8_t bit = 0; bit < 8; ++bit) {
            if (crc & 0x8000U) {
                crc = static_cast<uint16_t>((crc << 1) ^ 0x1021U);
            } else {
                crc = static_cast<uint16_t>(crc << 1);
            }
        }
    }
    return crc;
}

// --- Клас приймача та парсера телеметрії ---
class TelemetryReceiver {
public:
    enum class State : uint8_t {
        WaitStart,
        ReadPayload,
        ReadCrcLow,
        ReadCrcHigh,
        WaitEnd
    };

    void on_uart_rx_isr(uint8_t byte) noexcept {
        rx_buffer_.push(byte);
    }

    template <typename Callback>
    void poll(Callback&& packet_callback) noexcept {
        while (auto byte_opt = rx_buffer_.pop()) {
            const uint8_t byte = *byte_opt;
            switch (state_) {
                case State::WaitStart:
                    if (byte == FRAME_START_BYTE) {
                        bytes_read_ = 0;
                        state_ = State::ReadPayload;
                    }
                    break;

                case State::ReadPayload:
                    payload_raw_[bytes_read_++] = byte;
                    if (bytes_read_ >= PAYLOAD_SIZE) {
                        state_ = State::ReadCrcLow;
                    }
                    break;

                case State::ReadCrcLow:
                    rx_crc_ = byte;
                    state_ = State::ReadCrcHigh;
                    break;

                case State::ReadCrcHigh:
                    rx_crc_ |= static_cast<uint16_t>(static_cast<uint16_t>(byte) << 8);
                    state_ = State::WaitEnd;
                    break;

                case State::WaitEnd:
                    if (byte == FRAME_END_BYTE) {
                        const uint16_t calc_crc = calculate_crc16(payload_raw_);
                        if (calc_crc == rx_crc_) {
                            TelemetryPayload packet{};
                            std::memcpy(&packet, payload_raw_.data(), sizeof(packet));
                            packets_received_++;
                            packet_callback(packet);
                        } else {
                            crc_errors_++;
                        }
                    }
                    state_ = State::WaitStart;
                    break;
            }
        }
    }

    [[nodiscard]] uint32_t packets_received() const noexcept { return packets_received_; }
    [[nodiscard]] uint32_t crc_errors() const noexcept { return crc_errors_; }

private:
    StaticRingBuffer<uint8_t, 256> rx_buffer_{};
    State state_{State::WaitStart};
    std::array<uint8_t, PAYLOAD_SIZE> payload_raw_{};
    size_t bytes_read_{0};
    uint16_t rx_crc_{0};
    uint32_t packets_received_{0};
    uint32_t crc_errors_{0};
};
