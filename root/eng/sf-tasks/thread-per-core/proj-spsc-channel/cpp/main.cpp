#include <iostream>
#include <vector>
#include <array>
#include <atomic>
#include <span>
#include <memory>
#include <thread>
#include <cstdint>
#include <stdexcept>
#include <pthread.h>
#include <sched.h>

namespace tpc {

constexpr size_t CACHELINE_SIZE = 64;

struct CrossCoreMessage {
    uint32_t sender_core{0};
    uint32_t message_id{0};
    uint64_t payload{0};
};

template <typename T, size_t Capacity>
requires ((Capacity & (Capacity - 1)) == 0) // Ємність має бути степенем двійки
class alignas(CACHELINE_SIZE) SpscRingBuffer {
public:
    SpscRingBuffer() noexcept 
        : head_{0}, cached_tail_{0}, tail_{0}, cached_head_{0} {}

    // Заборона копіювання та переміщення для захисту прив'язки пам'яті
    SpscRingBuffer(const SpscRingBuffer&) = delete;
    SpscRingBuffer& operator=(const SpscRingBuffer&) = delete;

    [[nodiscard]] bool push(const T& item) noexcept {
        const size_t current_tail = tail_.load(std::memory_order_relaxed);

        if (current_tail - cached_head_ >= Capacity) {
            cached_head_ = head_.load(std::memory_order_acquire);
            if (current_tail - cached_head_ >= Capacity) {
                return false; // Буфер переповнений
            }
        }

        buffer_[current_tail & Mask] = item;
        tail_.store(current_tail + 1, std::memory_order_release);
        return true;
    }

    [[nodiscard]] size_t pop_batch(std::span<T> out_items) noexcept {
        const size_t current_head = head_.load(std::memory_order_relaxed);

        if (current_head == cached_tail_) {
            cached_tail_ = tail_.load(std::memory_order_acquire);
            if (current_head == cached_tail_) {
                return 0; // Немає доступних елементів
            }
        }

        const size_t available = cached_tail_ - current_head;
        const size_t to_read = std::min(available, out_items.size());

        for (size_t i = 0; i < to_read; ++i) {
            out_items[i] = buffer_[(current_head + i) & Mask];
        }

        head_.store(current_head + to_read, std::memory_order_release);
        return to_read;
    }

private:
    static constexpr size_t Mask = Capacity - 1;

    // Зона споживача (окрема кеш-лінія)
    alignas(CACHELINE_SIZE) std::atomic<size_t> head_;
    alignas(CACHELINE_SIZE) size_t cached_tail_;

    // Зона виробника (окрема кеш-лінія)
    alignas(CACHELINE_SIZE) std::atomic<size_t> tail_;
    alignas(CACHELINE_SIZE) size_t cached_head_;

    // Буфер елементів
    alignas(CACHELINE_SIZE) std::array<T, Capacity> buffer_{};
};

// RAII обгортка фіксації потоку на фізичному ядрі
class ScopedCorePinning {
public:
    explicit ScopedCorePinning(int core_id) {
        cpu_set_t cpuset;
        CPU_ZERO(&cpuset);
        CPU_SET(core_id, &cpuset);
        const int rc = pthread_setaffinity_np(pthread_self(), sizeof(cpu_set_t), &cpuset);
        if (rc != 0) {
            throw std::runtime_error("Не вдалося зафіксувати потік на ядрі");
        }
    }
};

} // namespace tpc
