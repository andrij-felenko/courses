#include <cstdint>
#include <array>
#include <optional>
#include <atomic>
#include <span>
#include <algorithm>

namespace embedded::sensor {

enum class SensorTag : uint8_t {
    Empty     = 0x00,
    GyroNC    = 0x01,
    AccelNC   = 0x02,
    Timestamp = 0x04,
    Invalid   = 0xFF
};

struct ImuSample {
    int16_t x{0};
    int16_t y{0};
    int16_t z{0};
    uint32_t timestamp_us{0};
};

template <typename T, size_t Capacity>
class LockFreeRingBuffer {
public:
    bool push(const T& item) noexcept {
        const auto current_head = head_.load(std::memory_order_relaxed);
        const auto next_head = (current_head + 1) % Capacity;
        if (next_head == tail_.load(std::memory_order_acquire)) {
            dropped_count_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }
        storage_[current_head] = item;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    std::optional<T> pop() noexcept {
        const auto current_tail = tail_.load(std::memory_order_relaxed);
        if (current_tail == head_.load(std::memory_order_acquire)) {
            return std::nullopt;
        }
        T item = storage_[current_tail];
        tail_.store((current_tail + 1) % Capacity, std::memory_order_release);
        return item;
    }

    [[nodiscard]] uint32_t dropped_count() const noexcept {
        return dropped_count_.load(std::memory_order_relaxed);
    }

private:
    std::array<T, Capacity> storage_{};
    std::atomic<size_t> head_{0};
    std::atomic<size_t> tail_{0};
    std::atomic<uint32_t> dropped_count_{0};
};

class FifoDmaReader {
public:
    static constexpr size_t SlotSize = 7;
    static constexpr size_t WatermarkSlots = 64;
    static constexpr size_t DmaBufferSize = WatermarkSlots * SlotSize + 1;

    FifoDmaReader() = default;

    void on_watermark_isr() noexcept {
        if (!dma_busy_.exchange(true, std::memory_order_acq_rel)) {
            tx_buffer_[0] = 0x78 | 0x80; // FIFO_DATA_OUT | SPI Read Bit
            std::fill(tx_buffer_.begin() + 1, tx_buffer_.end(), 0x00);
            
            start_hardware_dma(tx_buffer_.data(), rx_buffer_.data(), DmaBufferSize);
        }
    }

    void on_dma_complete_callback(uint32_t current_time_us) noexcept {
        stop_hardware_spi();
        invalidate_dcache(rx_buffer_.data(), DmaBufferSize);
        dma_busy_.store(false, std::memory_order_release);

        std::span<const uint8_t> payload{&rx_buffer_[1], DmaBufferSize - 1};

        for (size_t offset = 0; offset + SlotSize <= payload.size(); offset += SlotSize) {
            auto slot = payload.subspan(offset, SlotSize);
            auto tag = parse_tag(slot[0]);

            if (tag == SensorTag::Empty) {
                break;
            }

            if (tag == SensorTag::Invalid) {
                trigger_hardware_fifo_reset();
                break;
            }

            ImuSample sample{
                .x = static_cast<int16_t>(slot[1] | (static_cast<uint16_t>(slot[2]) << 8)),
                .y = static_cast<int16_t>(slot[3] | (static_cast<uint16_t>(slot[4]) << 8)),
                .z = static_cast<int16_t>(slot[5] | (static_cast<uint16_t>(slot[6]) << 8)),
                .timestamp_us = current_time_us
            };

            if (tag == SensorTag::AccelNC) {
                accel_queue_.push(sample);
            } else if (tag == SensorTag::GyroNC) {
                gyro_queue_.push(sample);
            }
        }
    }

    LockFreeRingBuffer<ImuSample, 256>& accel_queue() noexcept { return accel_queue_; }
    LockFreeRingBuffer<ImuSample, 256>& gyro_queue() noexcept { return gyro_queue_; }

private:
    [[nodiscard]] static SensorTag parse_tag(uint8_t raw_byte) noexcept {
        uint8_t tag_val = (raw_byte >> 3) & 0x1F;
        switch (tag_val) {
            case 0x00: return SensorTag::Empty;
            case 0x01: return SensorTag::GyroNC;
            case 0x02: return SensorTag::AccelNC;
            case 0x04: return SensorTag::Timestamp;
            default:   return SensorTag::Invalid;
        }
    }

    // Низькорівневі апаратні функції платформи
    void start_hardware_dma(const uint8_t* tx, uint8_t* rx, size_t len) noexcept;
    void stop_hardware_spi() noexcept;
    void trigger_hardware_fifo_reset() noexcept;
    void invalidate_dcache(const void* addr, size_t size) noexcept;

    alignas(32) std::array<uint8_t, DmaBufferSize> tx_buffer_{};
    alignas(32) std::array<uint8_t, DmaBufferSize> rx_buffer_{};
    std::atomic<bool> dma_busy_{false};

    LockFreeRingBuffer<ImuSample, 256> accel_queue_{};
    LockFreeRingBuffer<ImuSample, 256> gyro_queue_{};
};

} // namespace embedded::sensor
