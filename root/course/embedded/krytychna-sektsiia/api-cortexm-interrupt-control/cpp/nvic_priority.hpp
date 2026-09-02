#pragma once

/*
 * Пріоритет як тип, а не як число.
 *
 * У C поріг для BASEPRI — це макрос, і ніщо не заважає передати в регістр
 * сире 5 замість 0x50. Тут значення порогу можна отримати лише через
 * фабрику, яка сама зсуває біти, а помилковий пріоритет ловиться на
 * компіляції: consteval-функція викликає неоголошену дію й не збирається.
 */

#include "stm32f4xx.h"   /* __NVIC_PRIO_BITS, SCB, NVIC_* */

#include <cstdint>
#include <optional>

namespace cortexm {

inline constexpr std::uint32_t kPrioBits = static_cast<std::uint32_t>(__NVIC_PRIO_BITS);
inline constexpr std::uint32_t kPrioShift = 8U - kPrioBits;
inline constexpr std::uint8_t  kLowestPriority = static_cast<std::uint8_t>((1U << kPrioBits) - 1U);

class Basepri;
consteval Basepri basepri(std::uint8_t priority);
constexpr std::optional<Basepri> checked_basepri(std::uint8_t priority) noexcept;

/* Навмисно без визначення: виклик у consteval-контексті — помилка компіляції. */
void priority_out_of_range();

class Basepri {
public:
    [[nodiscard]] constexpr std::uint32_t raw() const noexcept { return raw_; }

    [[nodiscard]] constexpr std::uint8_t priority() const noexcept
    {
        return static_cast<std::uint8_t>(raw_ >> kPrioShift);
    }

private:
    friend consteval Basepri basepri(std::uint8_t);
    friend constexpr std::optional<Basepri> checked_basepri(std::uint8_t) noexcept;

    constexpr explicit Basepri(std::uint32_t raw) noexcept : raw_{raw} {}

    std::uint32_t raw_;
};

/*
 * Пріоритет 0 сюди не пройде: BASEPRI == 0 вимикає фільтрацію взагалі,
 * тобто найтерміновіше переривання порогом не маскується в принципі.
 */
consteval Basepri basepri(std::uint8_t priority)
{
    if (priority == 0U || priority > kLowestPriority) {
        priority_out_of_range();
    }
    return Basepri{static_cast<std::uint32_t>(priority) << kPrioShift};
}

/* Для пріоритету, відомого лише під час роботи (конфіг у флеші, параметр). */
constexpr std::optional<Basepri> checked_basepri(std::uint8_t priority) noexcept
{
    if (priority == 0U || priority > kLowestPriority) {
        return std::nullopt;
    }
    return Basepri{static_cast<std::uint32_t>(priority) << kPrioShift};
}

#if (__NVIC_PRIO_BITS == 4)
static_assert(basepri(5).raw() == 0x50U, "Пріоритет 5 при 4 бітах — це байт 0x50");
static_assert(basepri(5).priority() == 5U, "Зворотне перетворення має збігатися");
static_assert(!checked_basepri(0).has_value(), "Пріоритет 0 порогом не маскується");
#endif

/* Скільки бітів пріоритету зараз віддано під витіснення. */
[[nodiscard]] inline std::uint32_t preempt_bits() noexcept
{
    const std::uint32_t prigroup = NVIC_GetPriorityGrouping();
    const std::uint32_t preempt = (prigroup >= 7U) ? 0U : (7U - prigroup);
    return (preempt > kPrioBits) ? kPrioBits : preempt;
}

/*
 * BASEPRI ігнорує PRIGROUP і порівнює повний байт пріоритету. Тому єдине
 * групування, за якого поріг читається однозначно, — усі біти витісняючі.
 */
inline void use_flat_priority_grouping() noexcept
{
    NVIC_SetPriorityGrouping(7U - kPrioBits);
}

[[nodiscard]] inline bool priority_grouping_is_flat() noexcept
{
    return preempt_bits() == kPrioBits;
}

}  // namespace cortexm
