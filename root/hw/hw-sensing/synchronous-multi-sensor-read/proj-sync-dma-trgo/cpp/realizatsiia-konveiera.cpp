#include <cstdint>
#include <array>
#include <span>
#include <atomic>
#include <optional>
#include <concepts>

namespace sensor_sync {

inline constexpr std::size_t PacketSize = 14;
inline constexpr std::size_t RingCapacity = 64;

struct ImuRawReading {
    std::uint32_t timestamp_us{0};
    std::array<std::int16_t, 3> accel{0, 0, 0};
    std::array<std::int16_t, 3> gyro{0, 0, 0};
    std::int16_t temperature{0};
    std::uint8_t sensor_id{0};
    std::uint8_t flags{0};
};

template <typename T, std::size_t Capacity>
class LockFreeRingBuffer {
public:
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of two");

    constexpr LockFreeRingBuffer() : head_{0}, tail_{0} {}

    bool push(const T& item) noexcept {
        const auto current_head = head_.load(std::memory_order_relaxed);
        const auto next_head = (current_head + 1) & BufferMask;

        if (next_head == tail_.load(std::memory_order_acquire)) {
            return false; // Буфер переповнено
        }

        storage_[current_head] = item;
        head_.store(next_head, std::memory_order_release);
        return true;
    }

    std::optional<T> pop() noexcept {
        const auto current_tail = tail_.load(std::memory_order_relaxed);
        if (current_tail == head_.load(std::memory_order_acquire)) {
            return std::nullopt; // Буфер порожній
        }

        T item = storage_[current_tail];
        tail_.store((current_tail + 1) & BufferMask, std::memory_order_release);
        return item;
    }

    [[nodiscard]] bool empty() const noexcept {
        return head_.load(std::memory_order_relaxed) == tail_.load(std::memory_order_relaxed);
    }

private:
    static constexpr std::size_t BufferMask = Capacity - 1;
    std::array<T, Capacity> storage_{};
    std::atomic<std::size_t> head_{0};
    std::atomic<std::size_t> tail_{0};
};

class SpiDmaSyncReader {
public:
    explicit constexpr SpiDmaSyncReader(std::uint8_t sensor_id) noexcept
        : sensor_id_{sensor_id} {}

    void on_drdy_trigger(std::uint32_t captured_timestamp_us) noexcept {
        last_timestamp_ = captured_timestamp_us;
        start_dma_transfer();
    }

    void on_dma_complete(std::span<const std::uint8_t, PacketSize> rx_bytes,
                         LockFreeRingBuffer<ImuRawReading, RingCapacity>& queue) noexcept {
        ImuRawReading reading;
        reading.timestamp_us = last_timestamp_;
        reading.sensor_id = sensor_id_;

        // Декодування 16-бітних слів Big-Endian
        reading.accel[0] = static_cast<std::int16_t>((rx_bytes[1] << 8) | rx_bytes[2]);
        reading.accel[1] = static_cast<std::int16_t>((rx_bytes[3] << 8) | rx_bytes[4]);
        reading.accel[2] = static_cast<std::int16_t>((rx_bytes[5] << 8) | rx_bytes[6]);

        reading.temperature = static_cast<std::int16_t>((rx_bytes[7] << 8) | rx_bytes[8]);

        reading.gyro[0] = static_cast<std::int16_t>((rx_bytes[9] << 8) | rx_bytes[10]);
        reading.gyro[1] = static_cast<std::int16_t>((rx_bytes[11] << 8) | rx_bytes[12]);
        reading.gyro[2] = static_cast<std::int16_t>((rx_bytes[13] << 8) | rx_bytes[14]);

        queue.push(reading);
    }

private:
    void start_dma_transfer() noexcept {
        // Активація транзакції DMA через регістри периферії
    }

    std::uint8_t sensor_id_{0};
    std::uint32_t last_timestamp_{0};
};

} // namespace sensor_sync
