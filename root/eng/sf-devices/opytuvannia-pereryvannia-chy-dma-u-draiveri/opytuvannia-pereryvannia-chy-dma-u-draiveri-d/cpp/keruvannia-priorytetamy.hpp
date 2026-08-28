#include <cstdint>

class CriticalSectionGuard {
private:
    uint32_t prev_basepri_{0};
    static constexpr uint32_t MaxSyscallPriority = 0x50;

public:
    CriticalSectionGuard() noexcept {
        asm volatile (
            "mrs %0, basepri\n"
            "msr basepri, %1\n"
            "isb\n"
            : "=r" (prev_basepri_)
            : "r" (MaxSyscallPriority)
            : "memory"
        );
    }

    ~CriticalSectionGuard() noexcept {
        asm volatile (
            "msr basepri, %0\n"
            "isb\n"
            :
            : "r" (prev_basepri_)
            : "memory"
        );
    }

    CriticalSectionGuard(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard& operator=(const CriticalSectionGuard&) = delete;
};
