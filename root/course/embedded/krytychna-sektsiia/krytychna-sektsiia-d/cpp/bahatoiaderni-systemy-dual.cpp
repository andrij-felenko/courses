#include "critical_section.hpp"
#include <cstdint>

inline auto* const SIO_SPINLOCK0 = reinterpret_cast<volatile std::uint32_t*>(0xD0000100UL);

class [[nodiscard]] DualCoreGuard {
public:
    DualCoreGuard() noexcept {
        // 1. Захист локального ядра
        local_lock_ = embedded::sync::PrimaskLockPolicy::enter();
        
        // 2. Захоплення апаратного між'ядерного спінлока
        while (*SIO_SPINLOCK0 == 0U) {
            // Очікування
        }
    }

    ~DualCoreGuard() noexcept {
        // 3. Звільнення спінлока
        *SIO_SPINLOCK0 = 1U;
        
        // 4. Відновлення локальних переривань
        embedded::sync::PrimaskLockPolicy::exit(local_lock_);
    }

    DualCoreGuard(const DualCoreGuard&) = delete;
    DualCoreGuard& operator=(const DualCoreGuard&) = delete;

private:
    std::uint32_t local_lock_;
};
