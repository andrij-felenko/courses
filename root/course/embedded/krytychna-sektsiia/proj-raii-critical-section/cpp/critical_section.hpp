#pragma once

/*
 * RAII-вартові критичних секцій для Cortex-M.
 *
 * Заголовок свідомо ділиться навпіл: узагальнений вартовий, який нічого не
 * знає про залізо, і політики блокування Cortex-M. Через це той самий
 * вартовий складається й на хості, де політику підміняє заглушка.
 */

#include <atomic>
#include <concepts>
#include <cstddef>
#include <cstdint>
#include <utility>

#if defined(__ARM_ARCH)
#  include "cmsis_compiler.h"
#endif

namespace embedded::sync {

/* Компіляторний бар'єр: жодної інструкції, лише заборона переставляти
   доступи до пам'яті через межу секції. */
inline void memory_barrier() noexcept
{
    std::atomic_signal_fence(std::memory_order_seq_cst);
}

/* Контракт політики: зберегти стан маски при вході й відновити при виході.
   Обидві операції мусять бути noexcept — деструктор вартового не має права
   кинути виняток під час розкрутки стека. */
template <typename P>
concept LockPolicy = requires(typename P::StateType state) {
    { P::enter() } noexcept -> std::same_as<typename P::StateType>;
    { P::exit(state) } noexcept;
};

template <LockPolicy Policy>
class [[nodiscard]] CriticalSectionGuard {
public:
    CriticalSectionGuard() noexcept : state_{Policy::enter()} {}

    /* Деструктор працює на будь-якому виході: кінець блоку, return,
       break і навіть розкрутка стека винятком. */
    ~CriticalSectionGuard() noexcept { Policy::exit(state_); }

    /* Вартовий прив'язаний до свого стекового кадру: ні копії, ні переміщення. */
    CriticalSectionGuard(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard& operator=(const CriticalSectionGuard&) = delete;
    CriticalSectionGuard(CriticalSectionGuard&&) = delete;
    CriticalSectionGuard& operator=(CriticalSectionGuard&&) = delete;

private:
    typename Policy::StateType state_;
};

/* Адаптер під концепт BasicLockable: годиться для std::lock_guard
   і std::scoped_lock, коли блокування треба передати чужому коду. */
template <LockPolicy Policy>
class InterruptSpinLock {
public:
    void lock() noexcept { state_ = Policy::enter(); }
    void unlock() noexcept { Policy::exit(state_); }

private:
    typename Policy::StateType state_{};
};

/* Виконати дію під блокуванням і повернути її результат: значення
   обчислюється до знищення вартового, тобто ще під маскою. */
template <LockPolicy Policy, typename F>
decltype(auto) with_critical(F&& action)
{
    const CriticalSectionGuard<Policy> guard;
    return std::forward<F>(action)();
}

#if defined(__ARM_ARCH)

/* --- Політика 1: глобальне маскування PRIMASK (усі ядра Cortex-M) -------- */

class PrimaskLockPolicy {
public:
    using StateType = std::uint32_t;

    [[nodiscard]] static StateType enter() noexcept
    {
        const StateType saved = __get_PRIMASK();
        __disable_irq();
        memory_barrier();
        return saved;
    }

    static void exit(StateType saved) noexcept
    {
        memory_barrier();
        /* Відновлюємо, а не вмикаємо: вкладення довільної глибини безпечне. */
        __set_PRIMASK(saved);
    }
};
static_assert(LockPolicy<PrimaskLockPolicy>);

using IrqGuard = CriticalSectionGuard<PrimaskLockPolicy>;

/* --- Політика 2: селективне маскування BASEPRI (M3/M4/M7/M33) ------------ */

#if defined(__ARM_ARCH_7M__) || defined(__ARM_ARCH_7EM__) || defined(__ARM_ARCH_8M_MAIN__)

template <std::uint32_t MaxSyscallPriority>
class BasepriLockPolicy {
    static_assert(MaxSyscallPriority != 0U,
                  "BASEPRI = 0 вимикає маскування взагалі — це не критична секція");

public:
    using StateType = std::uint32_t;

    [[nodiscard]] static StateType enter() noexcept
    {
        const StateType saved = __get_BASEPRI();
        /* Поріг подано зміщеним у старші біти поля пріоритету NVIC.
           __set_BASEPRI_MAX лише посилює маскування, ніколи не послаблює. */
        __set_BASEPRI_MAX(MaxSyscallPriority);
        memory_barrier();
        return saved;
    }

    static void exit(StateType saved) noexcept
    {
        memory_barrier();
        __set_BASEPRI(saved);
    }
};

/* PriorityGuard<0x50> lock; — швидкі ISR із пріоритетом вище 5 не гальмуються. */
template <std::uint32_t Threshold>
using PriorityGuard = CriticalSectionGuard<BasepriLockPolicy<Threshold>>;

static_assert(LockPolicy<BasepriLockPolicy<0x50U>>);

#endif  // BASEPRI

/* IPSR != 0 означає, що ядро зараз обробляє виняток або переривання. */
[[nodiscard]] inline bool in_interrupt_context() noexcept
{
    return __get_IPSR() != 0U;
}

/* --- Cortex-M7: буфер, який після секції читає DMA ------------------------ */
/*
 * Блок живий лише тоді, коли перед цим заголовком підключено заголовок
 * пристрою: __DCACHE_PRESENT і SCB_CleanDCache_by_Addr оголошено в core_cm7.h.
 */
#if defined(__DCACHE_PRESENT) && (__DCACHE_PRESENT == 1U)

#if !defined(__SCB_DCACHE_LINE_SIZE)
#  define __SCB_DCACHE_LINE_SIZE 32U
#endif

template <LockPolicy Policy = PrimaskLockPolicy>
class [[nodiscard]] DmaBufferGuard {
public:
    DmaBufferGuard(const void* buffer, std::size_t size) noexcept
        : buffer_{buffer}, size_{size}, state_{Policy::enter()} {}

    ~DmaBufferGuard() noexcept
    {
        /* Свіжі байти можуть лежати в L1 D-Cache, а DMA ходить по шині
           просто в ОЗП. Виштовхуємо рядки кешу ДО того, як переривання
           ввімкнено назад; межі вирівнюємо на рядок, як вимагає CMSIS. */
        constexpr std::uintptr_t line = __SCB_DCACHE_LINE_SIZE;
        const auto base  = reinterpret_cast<std::uintptr_t>(buffer_);
        const auto start = base & ~(line - 1U);
        const auto end   = (base + size_ + line - 1U) & ~(line - 1U);

        SCB_CleanDCache_by_Addr(reinterpret_cast<std::uint32_t*>(start),
                                static_cast<std::int32_t>(end - start));
        __DSB();
        Policy::exit(state_);
    }

    DmaBufferGuard(const DmaBufferGuard&) = delete;
    DmaBufferGuard& operator=(const DmaBufferGuard&) = delete;
    DmaBufferGuard(DmaBufferGuard&&) = delete;
    DmaBufferGuard& operator=(DmaBufferGuard&&) = delete;

private:
    const void* buffer_;
    std::size_t size_;
    typename Policy::StateType state_;
};

#endif  // __DCACHE_PRESENT
#endif  // __ARM_ARCH

}  // namespace embedded::sync
