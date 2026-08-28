// Ідіоматична реалізація на C++ (C++20 std::atomic та RAII)
#include <iostream>
#include <atomic>
#include <thread>
#include <vector>
#include <concepts>
#include <new>

#if defined(__x86_64__) || defined(__i386__)
#include <immintrin.h>
#endif

class alignas(64) Seqlock {
private:
    std::atomic<uint32_t> seq_{0};
    std::atomic_flag writer_flag_{};   // C++20: типізована ініціалізація у стан «вільно»

public:
    Seqlock() = default;

    Seqlock(const Seqlock&) = delete;
    Seqlock& operator=(const Seqlock&) = delete;

    void write_lock() noexcept {
        while (writer_flag_.test_and_set(std::memory_order_acquire)) {
#if defined(__x86_64__) || defined(__i386__)
            _mm_pause();
#endif
        }
        const uint32_t current = seq_.load(std::memory_order_relaxed);
        seq_.store(current + 1, std::memory_order_relaxed);
        // аналог smp_wmb(): записи в дані не можуть випередити інкремент лічильника
        std::atomic_thread_fence(std::memory_order_release);
    }

    void write_unlock() noexcept {
        const uint32_t current = seq_.load(std::memory_order_relaxed);
        seq_.store(current + 1, std::memory_order_release);
        writer_flag_.clear(std::memory_order_release);
    }

    [[nodiscard]] uint32_t read_begin() const noexcept {
        uint32_t s;
        for (;;) {
            s = seq_.load(std::memory_order_acquire);
            if ((s & 1U) == 0) {
                break;
            }
#if defined(__x86_64__) || defined(__i386__)
            _mm_pause();
#endif
        }
        return s;
    }

    [[nodiscard]] bool read_retry(uint32_t start_seq) const noexcept {
        std::atomic_thread_fence(std::memory_order_acquire);
        return seq_.load(std::memory_order_relaxed) != start_seq;
    }
};

// RAII Обгортка для безпечного запису
class SeqlockWriterGuard {
private:
    Seqlock& lock_;
public:
    explicit SeqlockWriterGuard(Seqlock& lock) : lock_(lock) {
        lock_.write_lock();
    }
    ~SeqlockWriterGuard() {
        lock_.write_unlock();
    }
};
