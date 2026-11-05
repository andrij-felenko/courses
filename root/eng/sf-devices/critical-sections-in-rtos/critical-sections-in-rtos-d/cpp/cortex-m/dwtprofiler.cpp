#include <cstdint>
#include <atomic>

namespace diagnostics {

/* Регістри апаратного блоку DWT ядра Cortex-M */
inline volatile uint32_t& CoreDemcr()   { return *reinterpret_cast<volatile uint32_t*>(0xE000EDFC); }
inline volatile uint32_t& DwtControl()  { return *reinterpret_cast<volatile uint32_t*>(0xE0001000); }
inline volatile uint32_t& DwtCycleCnt() { return *reinterpret_cast<volatile uint32_t*>(0xE0001004); }
inline volatile uint32_t& GpioBsrr()    { return *reinterpret_cast<volatile uint32_t*>(0x40020418); }

class DwtProfiler {
public:
    static void init() noexcept {
        CoreDemcr() |= (1UL << 24);
        DwtCycleCnt() = 0;
        DwtControl() |= (1UL << 0);
    }

    static inline uint32_t getCycles() noexcept {
        return DwtCycleCnt();
    }
};

/* Діагностичний RAII вартовий із контролем граничного часу та виводом GPIO */
template <uint32_t MaxCyclesBudget = 840>
class TimedCriticalGuard {
public:
    inline TimedCriticalGuard() noexcept {
        // Сигналізація на фізичний вивід для осцилографа
        GpioBsrr() = (1UL << 5);

        std::atomic_signal_fence(std::memory_order_seq_cst);
        __asm__ volatile ("mrs %0, basepri" : "=r" (saved_basepri_));
        __asm__ volatile ("msr basepri, %0" :: "r" (0x50) : "memory");
        __asm__ volatile ("dsb 0xF" ::: "memory");
        __asm__ volatile ("isb 0xF" ::: "memory");
        std::atomic_signal_fence(std::memory_order_seq_cst);

        start_cycles_ = DwtProfiler::getCycles();
    }

    inline ~TimedCriticalGuard() noexcept {
        const uint32_t elapsed = DwtProfiler::getCycles() - start_cycles_;

        std::atomic_signal_fence(std::memory_order_seq_cst);
        __asm__ volatile ("dsb 0xF" ::: "memory");
        __asm__ volatile ("msr basepri, %0" :: "r" (saved_basepri_) : "memory");
        __asm__ volatile ("isb 0xF" ::: "memory");
        std::atomic_signal_fence(std::memory_order_seq_cst);

        // Опускання фізичного виводу
        GpioBsrr() = (1UL << (5 + 16));

        // Фіксація перевищення заданого бюджету часу
        if (elapsed > MaxCyclesBudget) {
            handleViolation(elapsed);
        }
    }

    TimedCriticalGuard(const TimedCriticalGuard&) = delete;
    TimedCriticalGuard& operator=(const TimedCriticalGuard&) = delete;

private:
    void handleViolation(uint32_t elapsed) noexcept {
        violations_count_++;
        worst_cycles_ = (elapsed > worst_cycles_) ? elapsed : worst_cycles_;
        // Апаратна точка зупину для дебагера
        __asm__ volatile ("bkpt #1");
    }

    uint32_t saved_basepri_{0};
    uint32_t start_cycles_{0};

    static inline uint32_t violations_count_{0};
    static inline uint32_t worst_cycles_{0};
};

} // namespace diagnostics
