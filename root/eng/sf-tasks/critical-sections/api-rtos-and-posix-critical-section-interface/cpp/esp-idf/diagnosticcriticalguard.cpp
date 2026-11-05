#include <cstdint>
#include <cstddef>

namespace sys::diag {

constexpr std::uint32_t kLatencyThresholdCycles = 800U;

// Діагностичний RAII-контролер затримок критичних секцій
class DiagnosticCriticalGuard final {
public:
    DiagnosticCriticalGuard(const char* file, std::uint32_t line) noexcept
        : file_(file), line_(line) {
        __asm__ __volatile__(
            "mrs %0, basepri \n\t"
            "msr basepri, %1 \n\t"
            "isb             \n\t"
            : "=r"(saved_mask_)
            : "r"(0x20)
            : "memory"
        );
        start_cycles_ = read_cyccnt();
    }

    ~DiagnosticCriticalGuard() noexcept {
        std::uint32_t elapsed = read_cyccnt() - start_cycles_;
        
        __asm__ __volatile__(
            "msr basepri, %0 \n\t"
            "isb             \n\t"
            :
            : "r"(saved_mask_)
            : "memory"
        );

        if (elapsed > kLatencyThresholdCycles) {
            on_latency_exceeded(file_, line_, elapsed);
        }
    }

    DiagnosticCriticalGuard(const DiagnosticCriticalGuard&) = delete;
    DiagnosticCriticalGuard& operator=(const DiagnosticCriticalGuard&) = delete;
    DiagnosticCriticalGuard(DiagnosticCriticalGuard&&) = delete;
    DiagnosticCriticalGuard& operator=(DiagnosticCriticalGuard&&) = delete;

private:
    static std::uint32_t read_cyccnt() noexcept {
        volatile std::uint32_t* cyccnt = reinterpret_cast<volatile std::uint32_t*>(0xE0001004);
        return *cyccnt;
    }

    static void on_latency_exceeded(const char* file, std::uint32_t line, std::uint32_t cycles) noexcept {
        // Обробка виявленого сплеску затримки
        (void)file;
        (void)line;
        (void)cycles;
    }

    const char* file_;
    std::uint32_t line_;
    std::uint32_t start_cycles_{0};
    std::uint32_t saved_mask_{0};
};

} // namespace sys::diag

#define DIAG_CRITICAL_GUARD_CPP() \
    ::sys::diag::DiagnosticCriticalGuard __diag_guard(__FILE__, __LINE__)
