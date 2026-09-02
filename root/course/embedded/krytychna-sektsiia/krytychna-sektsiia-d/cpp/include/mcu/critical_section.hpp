// RAII-вартовий критичної секції: конструктор входить, деструктор виходить.
// Жоден шлях виходу з функції — return, break, виняток — не може забути
// відновити маску, бо цим керує компілятор, а не дисципліна автора.
#pragma once

#include "mcu/primask_lock.hpp"

#if !defined(__ARM_ARCH_6M__)
#include "mcu/basepri_lock.hpp"
#endif

namespace mcu {

template <class Policy>
class [[nodiscard]] ScopedLock {
public:
    ScopedLock() noexcept : state_{Policy::enter()} {}
    ~ScopedLock() noexcept { Policy::exit(state_); }

    // Вартовий привʼязаний до свого стекового фрейму: ні копії, ні переміщення.
    ScopedLock(const ScopedLock&) = delete;
    ScopedLock& operator=(const ScopedLock&) = delete;
    ScopedLock(ScopedLock&&) = delete;
    ScopedLock& operator=(ScopedLock&&) = delete;

private:
    typename Policy::state_type state_;
};

// Повне маскування — коротко й на будь-якому ядрі Cortex-M.
using CriticalSectionGuard = ScopedLock<PrimaskLock>;

#if !defined(__ARM_ARCH_6M__)
// Маскування до порогу ОС: обробники 0..4 лишаються живими.
using RtosSectionGuard = ScopedLock<BasepriLock>;
#endif

// Використання:
//   {
//       const mcu::CriticalSectionGuard lock;  // саме ІМЕНОВАНИЙ обʼєкт
//       queue.push(sample);
//   }                                          // тут маска повернулася
//
// [[nodiscard]] ловить рівно одну помилку, зате смертельну:
//   mcu::CriticalSectionGuard{};  // тимчасовий обʼєкт помирає в цьому ж рядку,
//                                 // секція порожня, а код нижче вважає себе захищеним.

} // namespace mcu
