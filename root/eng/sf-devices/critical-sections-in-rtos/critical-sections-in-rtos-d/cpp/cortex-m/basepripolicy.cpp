#include <cstdint>
#include <atomic>

namespace kernel {

/* Апаратна політика селективного маскування Cortex-M */
struct BasepriPolicy {
    static constexpr uint32_t kMaxSyscallPriority = 0x50;

    static inline uint32_t lock() noexcept {
        std::atomic_signal_fence(std::memory_order_seq_cst);
        uint32_t prev_basepri;
        __asm__ volatile ("mrs %0, basepri" : "=r" (prev_basepri));
        __asm__ volatile ("msr basepri, %0" :: "r" (kMaxSyscallPriority) : "memory");
        __asm__ volatile ("dsb 0xF" ::: "memory");
        __asm__ volatile ("isb 0xF" ::: "memory");
        std::atomic_signal_fence(std::memory_order_seq_cst);
        return prev_basepri;
    }

    static inline void unlock(uint32_t prev_basepri) noexcept {
        std::atomic_signal_fence(std::memory_order_seq_cst);
        __asm__ volatile ("dsb 0xF" ::: "memory");
        __asm__ volatile ("msr basepri, %0" :: "r" (prev_basepri) : "memory");
        __asm__ volatile ("isb 0xF" ::: "memory");
        std::atomic_signal_fence(std::memory_order_seq_cst);
    }
};

/* Шаблонний RAII вартовий критичної секції з нульовими накладними витратами */
template <typename LockPolicy = BasepriPolicy>
class CriticalSectionGuard {
public:
    inline CriticalSectionGuard() noexcept 
        : saved_state_(LockPolicy::lock()) {}

    inline ~CriticalSectionGuard() noexcept {
        LockPolicy::unlock(saved_state_);
    }

    /* Заборона копіювання та переміщення для уникнення порушення симетрії входу/виходу */
    CriticalSectionGuard(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard& operator=(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard(CriticalSectionGuard&&) = delete;
    CriticalSectionGuard& operator=(CriticalSectionGuard&&) = delete;

private:
    const uint32_t saved_state_;
};

} // namespace kernel

/* Демонстрація безпечного використання в об'єктно-орієнтованому драйвері */
class TelemetryManager {
public:
    struct TelemetryData {
        int32_t axes[3];
        uint32_t timestamp;
        uint32_t sequence;
    };

    bool tryReadSnapshot(TelemetryData& out_data) noexcept {
        // Конструктор автоматично маскує переривання та зберігає стан
        kernel::CriticalSectionGuard guard;

        if (!is_calibrated_) {
            // Безпечний ранній вихід: деструктор guard гарантовано відновить BASEPRI
            return false;
        }

        out_data = raw_data_;
        return true;
        // При виході з області видимості деструктор відновлює попередній стан
    }

    void writeFromIsr(const TelemetryData& new_data) noexcept {
        kernel::CriticalSectionGuard guard;
        raw_data_ = new_data;
        is_calibrated_ = true;
    }

private:
    TelemetryData raw_data_{};
    bool is_calibrated_{false};
};
