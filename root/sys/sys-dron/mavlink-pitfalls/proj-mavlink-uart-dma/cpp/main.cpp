#include <cstdint>
#include <cstddef>
#include <array>
#include <span>
#include <atomic>
#include <concepts>

enum class PacketPriority : uint8_t {
    Low = 0,     // Потокова телеметрія: ATTITUDE, VFR_HUD
    Medium = 1,  // Навігація: GLOBAL_POSITION_INT
    High = 2     // Критичні кадри: HEARTBEAT, COMMAND_ACK
};

template <size_t Capacity>
class SafeRingBuffer {
    static_assert((Capacity & (Capacity - 1)) == 0, "Capacity must be a power of two for mask indexing");

public:
    SafeRingBuffer() : head_(0), tail_(0), dropped_count_(0) {}

    [[nodiscard]] size_t available() const noexcept {
        const size_t head = head_.load(std::memory_order_relaxed);
        const size_t tail = tail_.load(std::memory_order_relaxed);
        return (Capacity - 1) - ((head - tail) & (Capacity - 1));
    }

    bool push(std::span<const uint8_t> data, PacketPriority priority) noexcept {
        const size_t len = data.size();
        if (len == 0 || len >= Capacity) {
            return false;
        }

        const size_t free_slots = available();
        if (free_slots < len) {
            dropped_count_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }

        size_t head = head_.load(std::memory_order_relaxed);
        for (const uint8_t byte : data) {
            buffer_[head & (Capacity - 1)] = byte;
            head++;
        }
        head_.store(head, std::memory_order_release);
        return true;
    }

    std::span<const uint8_t> peek_contiguous_chunk() noexcept {
        const size_t head = head_.load(std::memory_order_acquire);
        const size_t tail = tail_.load(std::memory_order_relaxed);

        if (head == tail) {
            return {};
        }

        const size_t tail_idx = tail & (Capacity - 1);
        const size_t head_idx = head & (Capacity - 1);

        if (head_idx > tail_idx) {
            return std::span<const uint8_t>(&buffer_[tail_idx], head_idx - tail_idx);
        }
        return std::span<const uint8_t>(&buffer_[tail_idx], Capacity - tail_idx);
    }

    void advance_tail(size_t count) noexcept {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);
        tail_.store(current_tail + count, std::memory_order_release);
    }

    [[nodiscard]] size_t dropped_packets() const noexcept {
        return dropped_count_.load(std::memory_order_relaxed);
    }

private:
    std::array<uint8_t, Capacity> buffer_{};
    alignas(64) std::atomic<size_t> head_;
    alignas(64) std::atomic<size_t> tail_;
    std::atomic<size_t> dropped_count_;
};

class MavlinkAsyncUartDriver {
public:
    static constexpr size_t RxBufferSize = 512;
    static constexpr size_t TxRingSize = 1024;

    MavlinkAsyncUartDriver() = default;

    bool send_packet(std::span<const uint8_t> packet, PacketPriority prio) noexcept {
        const bool ok = tx_ring_.push(packet, prio);
        if (ok) {
            try_start_dma_tx();
        }
        return ok;
    }

    void on_tx_dma_complete(size_t bytes_transferred) noexcept {
        tx_ring_.advance_tail(bytes_transferred);
        tx_busy_.store(false, std::memory_order_release);
        try_start_dma_tx();
    }

    template <typename ParserCallback>
    void process_rx_dma(size_t dma_write_head, ParserCallback&& callback) noexcept {
        if (dma_write_head == last_rx_idx_) {
            return;
        }

        if (dma_write_head > last_rx_idx_) {
            for (size_t i = last_rx_idx_; i < dma_write_head; ++i) {
                callback(rx_dma_buffer_[i]);
            }
        } else {
            for (size_t i = last_rx_idx_; i < RxBufferSize; ++i) {
                callback(rx_dma_buffer_[i]);
            }
            for (size_t i = 0; i < dma_write_head; ++i) {
                callback(rx_dma_buffer_[i]);
            }
        }
        last_rx_idx_ = dma_write_head;
    }

private:
    void try_start_dma_tx() noexcept {
        bool expected = false;
        if (!tx_busy_.compare_exchange_strong(expected, true, std::memory_order_acq_rel)) {
            return;
        }

        auto chunk = tx_ring_.peek_contiguous_chunk();
        if (chunk.empty()) {
            tx_busy_.store(false, std::memory_order_release);
            return;
        }

        // Апаратний запуск DMA: chunk.data() та chunk.size()
        // launch_hardware_dma_tx(chunk.data(), chunk.size());
    }

    std::array<uint8_t, RxBufferSize> rx_dma_buffer_{};
    size_t last_rx_idx_{0};
    SafeRingBuffer<TxRingSize> tx_ring_{};
    std::atomic<bool> tx_busy_{false};
};
