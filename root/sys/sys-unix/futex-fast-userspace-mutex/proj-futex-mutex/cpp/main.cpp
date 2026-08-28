#include <iostream>
#include <atomic>
#include <cstdint>
#include <climits>
#include <unistd.h>
#include <sys/syscall.h>
#include <linux/futex.h>

namespace sys {

class futex_mutex {
public:
    enum class state : uint32_t {
        unlocked = 0,
        locked_no_waiters = 1,
        locked_with_waiters = 2
    };

    constexpr futex_mutex() noexcept : state_{0} {}

    void lock() noexcept {
        uint32_t expected = 0;
        // Швидкий шлях (Fast Path): 0 -> 1 у просторі користувача з аквізиційною семантикою
        if (state_.compare_exchange_strong(expected, 1, std::memory_order_acquire)) {
            return;
        }

        if (expected != 2) {
            expected = state_.exchange(2, std::memory_order_acquire);
        }

        while (expected != 0) {
            futex_wait(reinterpret_cast<uint32_t*>(&state_), 2);
            expected = state_.exchange(2, std::memory_order_acquire);
        }
    }

    void unlock() noexcept {
        // Релізна семантика вивантаження критичної секції
        if (state_.fetch_sub(1, std::memory_order_release) != 1) {
            state_.store(0, std::memory_order_release);
            futex_wake(reinterpret_cast<uint32_t*>(&state_), 1);
        }
    }

    uint32_t* native_handle() noexcept {
        return reinterpret_cast<uint32_t*>(&state_);
    }

private:
    static inline int futex_wait(uint32_t* uaddr, uint32_t val) noexcept {
        return ::syscall(SYS_futex, uaddr, FUTEX_WAIT_PRIVATE, val, nullptr, nullptr, 0);
    }

    static inline int futex_wake(uint32_t* uaddr, int count) noexcept {
        return ::syscall(SYS_futex, uaddr, FUTEX_WAKE_PRIVATE, count, nullptr, nullptr, 0);
    }

    std::atomic<uint32_t> state_;
};

// RAII обгортка для автоматичного керування блокуванням м'ютекса
class lock_guard {
public:
    explicit lock_guard(futex_mutex& m) : mutex_(m) {
        mutex_.lock();
    }
    ~lock_guard() {
        mutex_.unlock();
    }

    lock_guard(const lock_guard&) = delete;
    lock_guard& operator=(const lock_guard&) = delete;

private:
    futex_mutex& mutex_;
};

class futex_condvar {
public:
    constexpr futex_condvar() noexcept : sequence_{0} {}

    void wait(futex_mutex& m) noexcept {
        uint32_t seq = sequence_.load(std::memory_order_relaxed);
        m.unlock();
        futex_wait(reinterpret_cast<uint32_t*>(&sequence_), seq);
        m.lock();
    }

    void signal() noexcept {
        sequence_.fetch_add(1, std::memory_order_release);
        futex_wake(reinterpret_cast<uint32_t*>(&sequence_), 1);
    }

    void broadcast(futex_mutex& m) noexcept {
        uint32_t seq = sequence_.fetch_add(1, std::memory_order_release) + 1;
        futex_cmp_requeue(reinterpret_cast<uint32_t*>(&sequence_),
                          m.native_handle(), 1, INT_MAX, seq);
    }

private:
    static inline int futex_wait(uint32_t* uaddr, uint32_t val) noexcept {
        return ::syscall(SYS_futex, uaddr, FUTEX_WAIT_PRIVATE, val, nullptr, nullptr, 0);
    }

    static inline int futex_wake(uint32_t* uaddr, int count) noexcept {
        return ::syscall(SYS_futex, uaddr, FUTEX_WAKE_PRIVATE, count, nullptr, nullptr, 0);
    }

    static inline int futex_cmp_requeue(uint32_t* uaddr1, uint32_t* uaddr2,
                                       int wake_count, int requeue_count, uint32_t val3) noexcept {
        return ::syscall(SYS_futex, uaddr1, FUTEX_CMP_REQUEUE_PRIVATE,
                          wake_count, requeue_count, uaddr2, val3);
    }

    std::atomic<uint32_t> sequence_;
};

} // namespace sys
