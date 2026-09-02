#pragma once

namespace bumpless {

// Критична секція перемикання режиму.
//
// На Cortex-M це PRIMASK (__get_PRIMASK/__disable_irq/__set_PRIMASK), на RTOS —
// м'ютекс контексту регулятора. Тут — лічильник глибини: він дає задачам
// керування чесно спитати «чи не йде зараз транзакція?» і відкласти свій такт.
// Ручного unlock немає навмисно: розблокування прив'язане до часу життя.
class IrqGuard {
public:
    IrqGuard() noexcept : saved_{depth_}
    {
        depth_ = saved_ + 1u;
        ++lock_events_;
    }

    ~IrqGuard() { depth_ = saved_; } // відновлюємо, а не «просто вмикаємо»

    IrqGuard(const IrqGuard&) = delete;
    IrqGuard& operator=(const IrqGuard&) = delete;
    IrqGuard(IrqGuard&&) = delete;
    IrqGuard& operator=(IrqGuard&&) = delete;

    [[nodiscard]] static bool locked() noexcept { return depth_ > 0u; }
    [[nodiscard]] static unsigned lock_events() noexcept { return lock_events_; }
    [[nodiscard]] static unsigned deferred_ticks() noexcept { return deferred_ticks_; }

    // Швидкий контур, що застав замок узятим, рахує собі відкладений такт.
    static void note_deferred_tick() noexcept { ++deferred_ticks_; }

    static void reset_counters() noexcept
    {
        lock_events_ = 0u;
        deferred_ticks_ = 0u;
    }

private:
    unsigned saved_;
    inline static unsigned depth_{0u};
    inline static unsigned lock_events_{0u};
    inline static unsigned deferred_ticks_{0u};
};

} // namespace bumpless
