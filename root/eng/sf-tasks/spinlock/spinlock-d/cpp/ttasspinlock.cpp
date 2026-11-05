#include <atomic>
#if defined(__x86_64__) || defined(_M_X64) || defined(__i386__)
#include <emmintrin.h>
#endif

// Оптимізований спін-замок Test-and-Test-and-Set (TTAS)
class TtasSpinlock {
private:
    std::atomic<bool> flag_{false};

    inline void cpu_relax() noexcept {
#if defined(__x86_64__) || defined(_M_X64) || defined(__i386__)
        _mm_pause(); // Апаратна пауза процесора x86
#endif
    }

public:
    void lock() noexcept {
        while (true) {
            // Звичайне читання (Test) у стані Shared без атомарного запису
            if (!flag_.load(std::memory_order_relaxed)) {
                // Атомарне перемикання (Test-and-Set) лише при появі шанс захопити
                if (!flag_.exchange(true, std::memory_order_acquire)) {
                    return; // Замок успішно отримано
                }
            }
            // Зниження енергоспоживання та збереження ресурсів конвеєра
            cpu_relax();
        }
    }

    void unlock() noexcept {
        flag_.store(false, std::memory_order_release);
    }
};
