#include <cstdint>

// Ідіоматична RAII-обгортка критичної секції для C++
class InterruptLockGuard {
public:
    InterruptLockGuard() noexcept {
        #if defined(__ARM_ARCH)
        __asm volatile ("MRS %0, primask" : "=r" (saved_primask_) :: "memory");
        __asm volatile ("CPSID i" ::: "memory");
        #endif
    }

    ~InterruptLockGuard() noexcept {
        #if defined(__ARM_ARCH)
        __asm volatile ("MSR primask, %0" :: "r" (saved_primask_) : "memory");
        #endif
    }

    // Заборона копіювання та переміщення
    InterruptLockGuard(const InterruptLockGuard&) = delete;
    InterruptLockGuard& operator=(const InterruptLockGuard&) = delete;
    InterruptLockGuard(InterruptLockGuard&&) = delete;
    InterruptLockGuard& operator=(InterruptLockGuard&&) = delete;

private:
    std::uint32_t saved_primask_{0};
};

// Приклад безпечного оновлення 64-бітного таймера
inline volatile std::uint64_t g_system_ticks{0};

[[nodiscard]] std::uint64_t get_system_ticks_safe() noexcept {
    const InterruptLockGuard lock{};
    // Безпечне неподільне зчитування двох 32-бітних регістрів
    return g_system_ticks;
}
