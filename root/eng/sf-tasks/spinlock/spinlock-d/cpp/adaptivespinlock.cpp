#include <atomic>
#include <thread>

#if defined(__x86_64__) || defined(_M_X64) || defined(__i386__)
#include <emmintrin.h>
#define cpu_relax() _mm_pause()
#else
#define cpu_relax() ((void)0)
#endif

class AdaptiveSpinlock {
private:
    std::atomic<bool> locked_{false};
    static constexpr int kMaxSpins = 1000;

public:
    AdaptiveSpinlock() = default;

    void lock() noexcept {
        // 1. Етап швидкого активного очікування (Test-and-Test-and-Set)
        for (int spin = 0; spin < kMaxSpins; ++spin) {
            if (!locked_.load(std::memory_order_relaxed)) {
                if (!locked_.exchange(true, std::memory_order_acquire)) {
                    return; // Успішно захоплено без звернення до ядра
                }
            }
            cpu_relax();
        }

        // 2. Етап адаптивного переходу до планувальника операційної системи
        while (locked_.exchange(true, std::memory_order_acquire)) {
            std::this_thread::yield();
        }
    }

    void unlock() noexcept {
        locked_.store(false, std::memory_order_release);
    }

    // Забороняємо копіювання для збереження цілісності атомарного стану
    AdaptiveSpinlock(const AdaptiveSpinlock&) = delete;
    AdaptiveSpinlock& operator=(const AdaptiveSpinlock&) = delete;
};
