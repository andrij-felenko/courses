// Лічильники, яким критична секція не потрібна взагалі: std::atomic на ARMv7-M
// компілюється рівно в цикл LDREX/STREX, тому переривання не маскуються й
// жоден обробник не дістає затримки.
#pragma once

#include <atomic>
#include <cstdint>
#include <type_traits>

#include "mcu/critical_section.hpp"

namespace mcu {

class LockFreeCounter {
public:
    void add(std::uint32_t n) noexcept { value_.fetch_add(n, std::memory_order_relaxed); }

    void set_bits(std::uint32_t bits) noexcept { value_.fetch_or(bits, std::memory_order_relaxed); }

    [[nodiscard]] std::uint32_t value() const noexcept
    {
        return value_.load(std::memory_order_relaxed);
    }

    // Явний оптимістичний цикл — рівно те, що fetch_add робить усередині.
    // compare_exchange_weak сам оновить expected, коли монітор збило переривання.
    std::uint32_t add_saturating(std::uint32_t n, std::uint32_t limit) noexcept
    {
        std::uint32_t expected = value_.load(std::memory_order_relaxed);
        std::uint32_t desired = 0;
        do {
            desired = (limit - expected < n) ? limit : expected + n;
        } while (!value_.compare_exchange_weak(expected, desired, std::memory_order_relaxed,
                                               std::memory_order_relaxed));
        return desired;
    }

private:
    std::atomic<std::uint32_t> value_{0};
};

// Cortex-M0/M0+: монітора ексклюзивності немає, std::atomic<std::uint32_t> уже
// не lock-free — компілятор кличе бібліотечні функції. Там лічильник чесніше
// зібрати на критичній секції, ніж удавати, що вона не потрібна.
class GuardedCounter {
public:
    void add(std::uint32_t n) noexcept
    {
        const CriticalSectionGuard lock;
        value_ += n;
    }

    void set_bits(std::uint32_t bits) noexcept
    {
        const CriticalSectionGuard lock;
        value_ |= bits;
    }

    [[nodiscard]] std::uint32_t value() const noexcept
    {
        const CriticalSectionGuard lock;
        return value_;
    }

    std::uint32_t add_saturating(std::uint32_t n, std::uint32_t limit) noexcept
    {
        const CriticalSectionGuard lock;
        value_ = (limit - value_ < n) ? limit : value_ + n;
        return value_;
    }

private:
    std::uint32_t value_{0};
};

// Вибір робить компілятор, а не автор прошивки.
using PacketCounter = std::conditional_t<std::atomic<std::uint32_t>::is_always_lock_free,
                                         LockFreeCounter, GuardedCounter>;

} // namespace mcu
