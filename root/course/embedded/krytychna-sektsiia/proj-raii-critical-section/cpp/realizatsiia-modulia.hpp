#pragma once

#include <cstdint>
#include <concepts>
#include <type_traits>

#if defined(__ARMCC_VERSION) || defined(__GNUC__)
    #include "cmsis_compiler.h"
#else
    #error "Непідтримуваний компілятор: потрібна підтримка CMSIS intrinsics"
#endif

namespace embedded::sync {

// Бар'єр оптимізації компілятора
inline void memory_barrier() noexcept {
    __asm volatile("" ::: "memory");
}

// Діагностика контексту: перевірка, чи код виконується в обробнику переривання
[[nodiscard]] inline bool in_interrupt_context() noexcept {
    return (__get_IPSR() != 0U);
}

/* ========================================================================= */
/* 1. Політика блокування через PRIMASK (Глобальне вимкнення IRQ)           */
/* ========================================================================= */

class PrimaskLockPolicy {
public:
    using StateType = std::uint32_t;

    [[nodiscard]] static StateType enter() noexcept {
        const StateType state = __get_PRIMASK();
        __disable_irq();
        memory_barrier();
        return state;
    }

    static void exit(StateType state) noexcept {
        memory_barrier();
        __set_PRIMASK(state);
    }
};

/* ========================================================================= */
/* 2. Політика блокування через BASEPRI (Маскування за порогом пріоритету)   */
/* ========================================================================= */

#if (__CORTEX_M >= 3U) || defined(__ARM_ARCH_7M__) || defined(__ARM_ARCH_7EM__) || defined(__ARM_ARCH_8M_MAIN__)

template <std::uint8_t MaxSyscallPriority>
class BasepriLockPolicy {
public:
    using StateType = std::uint32_t;

    [[nodiscard]] static StateType enter() noexcept {
        const StateType state = __get_BASEPRI();
        __set_BASEPRI_MAX(MaxSyscallPriority);
        memory_barrier();
        return state;
    }

    static void exit(StateType state) noexcept {
        memory_barrier();
        __set_BASEPRI(state);
    }
};

#endif

/* ========================================================================= */
/* 3. Універсальний RAII-вартовий критичної секції (Critical Section Guard) */
/* ========================================================================= */

template <typename Policy = PrimaskLockPolicy>
class [[nodiscard]] CriticalSectionGuard {
public:
    CriticalSectionGuard() noexcept 
        : saved_state_(Policy::enter()) {}

    ~CriticalSectionGuard() noexcept {
        Policy::exit(saved_state_);
    }

    // Заборона копіювання та переміщення: вартовий жорстко прив'язаний до поточного стекового фрейму
    CriticalSectionGuard(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard& operator=(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard(CriticalSectionGuard&&) = delete;
    CriticalSectionGuard& operator=(CriticalSectionGuard&&) = delete;

private:
    typename Policy::StateType saved_state_;
};

// Зручний псевдонім для стандартного глобального захисту
using IrqGuard = CriticalSectionGuard<PrimaskLockPolicy>;

#if (__CORTEX_M >= 3U) || defined(__ARM_ARCH_7M__) || defined(__ARM_ARCH_7EM__) || defined(__ARM_ARCH_8M_MAIN__)
template <std::uint8_t PriorityThreshold>
using PriorityGuard = CriticalSectionGuard<BasepriLockPolicy<PriorityThreshold>>;
#endif

/* ========================================================================= */
/* 4. Адаптер під стандартний концепт BasicLockable (std::lock_guard)        */
/* ========================================================================= */

class InterruptSpinLock {
public:
    void lock() noexcept {
        saved_state_ = PrimaskLockPolicy::enter();
    }

    void unlock() noexcept {
        PrimaskLockPolicy::exit(saved_state_);
    }

private:
    std::uint32_t saved_state_{0};
};

} // namespace embedded::sync
