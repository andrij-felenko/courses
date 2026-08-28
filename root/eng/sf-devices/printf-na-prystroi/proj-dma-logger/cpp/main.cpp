#include <cstdint>
#include <cstddef>
#include <cstring>
#include <string_view>
#include <span>
#include <array>
#include <atomic>
#include <cstdio>
#include <cstdarg>

extern "C" void hw_uart_dma_start_transfer(const uint8_t *src, size_t length);
extern "C" void hw_enter_critical(void);
extern "C" void hw_exit_critical(void);
extern "C" void hw_dcache_clean_range(const void *addr, size_t size);

template <size_t BufferSize = 2048>
class DmaAsyncLogger {
    static_assert((BufferSize & (BufferSize - 1)) == 0, "Розмір буфера мусить бути степенем двійки!");
    static constexpr size_t BufferMask = BufferSize - 1;

public:
    constexpr DmaAsyncLogger() = default;

    void init() noexcept {
        head_.store(0, std::memory_order_relaxed);
        tail_.store(0, std::memory_order_relaxed);
        dma_active_len_ = 0;
        dma_busy_.store(false, std::memory_order_relaxed);
        dropped_bytes_.store(0, std::memory_order_relaxed);
    }

    size_t write(std::string_view message) noexcept {
        return write(std::span<const uint8_t>(reinterpret_cast<const uint8_t*>(message.data()), message.size()));
    }

    size_t write(std::span<const uint8_t> data) noexcept {
        if (data.empty()) {
            return 0;
        }

        CriticalSectionGuard lock;

        const size_t free_space = available_space();
        size_t bytes_to_write = data.size();

        if (bytes_to_write > free_space) {
            dropped_bytes_.fetch_add(bytes_to_write - free_space, std::memory_order_relaxed);
            bytes_to_write = free_space;
        }

        if (bytes_to_write == 0) {
            return 0;
        }

        const size_t cur_head = head_.load(std::memory_order_relaxed);
        const size_t first_part = BufferSize - cur_head;

        if (bytes_to_write <= first_part) {
            std::memcpy(&storage_[cur_head], data.data(), bytes_to_write);
            head_.store((cur_head + bytes_to_write) & BufferMask, std::memory_order_release);
        } else {
            std::memcpy(&storage_[cur_head], data.data(), first_part);
            std::memcpy(&storage_[0], data.data() + first_part, bytes_to_write - first_part);
            head_.store((bytes_to_write - first_part) & BufferMask, std::memory_order_release);
        }

        kick_dma_locked();
        return bytes_to_write;
    }

    int print_fmt(const char* fmt, ...) noexcept {
        std::array<char, 128> staging{};
        va_list args;
        va_start(args, fmt);
        const int len = vsnprintf(staging.data(), staging.size(), fmt, args);
        va_end(args);

        if (len > 0) {
            const size_t count = (static_cast<size_t>(len) < staging.size()) ? static_cast<size_t>(len) : (staging.size() - 1);
            write(std::string_view(staging.data(), count));
        }
        return len;
    }

    void on_dma_transfer_complete_isr() noexcept {
        const size_t cur_tail = tail_.load(std::memory_order_relaxed);
        tail_.store((cur_tail + dma_active_len_) & BufferMask, std::memory_order_release);
        dma_active_len_ = 0;
        dma_busy_.store(false, std::memory_order_relaxed);

        kick_dma_locked();
    }

    [[nodiscard]] uint32_t dropped_count() const noexcept {
        return dropped_bytes_.load(std::memory_order_relaxed);
    }

private:
    struct CriticalSectionGuard {
        CriticalSectionGuard() noexcept { hw_enter_critical(); }
        ~CriticalSectionGuard() noexcept { hw_exit_critical(); }
        CriticalSectionGuard(const CriticalSectionGuard&) = delete;
        CriticalSectionGuard& operator=(const CriticalSectionGuard&) = delete;
    };

    [[nodiscard]] size_t available_space() const noexcept {
        const size_t h = head_.load(std::memory_order_relaxed);
        const size_t t = tail_.load(std::memory_order_relaxed);
        if (h >= t) {
            return (BufferSize - 1) - (h - t);
        }
        return (t - h) - 1;
    }

    void kick_dma_locked() noexcept {
        if (dma_busy_.load(std::memory_order_relaxed)) {
            return;
        }

        const size_t h = head_.load(std::memory_order_relaxed);
        const size_t t = tail_.load(std::memory_order_relaxed);
        if (h == t) {
            return;
        }

        const size_t chunk_len = (h > t) ? (h - t) : (BufferSize - t);

        dma_busy_.store(true, std::memory_order_relaxed);
        dma_active_len_ = chunk_len;

        hw_dcache_clean_range(&storage_[t], chunk_len);
        hw_uart_dma_start_transfer(&storage_[t], chunk_len);
    }

    alignas(4) std::array<uint8_t, BufferSize> storage_{};
    std::atomic<size_t> head_{0};
    std::atomic<size_t> tail_{0};
    size_t dma_active_len_{0};
    std::atomic<bool> dma_busy_{false};
    std::atomic<uint32_t> dropped_bytes_{0};
};
