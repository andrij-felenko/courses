#include <cstdint>
#include <cstddef>
#include <atomic>

template <typename T, std::size_t Size>
class RingBufferSPSC {
    static_assert((Size & (Size - 1)) == 0, "Розмір буфера повинен бути степенем двійки");

public:
    RingBufferSPSC() : head_(0), tail_(0), overflow_count_(0) {}

    bool put(const T& item) {
        const auto current_head = head_.load(std::memory_order_relaxed);
        const auto next_head = (current_head + 1) & Mask;

        if (next_head == tail_.load(std::memory_order_acquire)) {
            overflow_count_.fetch_add(1, std::memory_order_relaxed);
            return false;
        }

        buffer_[current_head] = item;
        head_.store(next_head, std::memory_order_release); // Захоплення-вивільнення гарантує впорядкування
        return true;
    }

    bool get(T& item) {
        const auto current_tail = tail_.load(std::memory_order_relaxed);
        if (head_.load(std::memory_order_acquire) == current_tail) {
            return false;
        }

        item = buffer_[current_tail];
        tail_.store((current_tail + 1) & Mask, std::memory_order_release);
        return true;
    }

    std::size_t get_overflow_count() const {
        return overflow_count_.load(std::memory_order_relaxed);
    }

private:
    static constexpr std::size_t Mask = Size - 1;
    T buffer_[Size];
    std::atomic<std::size_t> head_;
    std::atomic<std::size_t> tail_;
    std::atomic<std::size_t> overflow_count_;
};
