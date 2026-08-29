// reg.hpp — типобезпечний доступ до регістрів периферії.
//
// У C регістр — це макрос REG32(addr), і компілятор не заперечить проти
// запису бітів TIM1 у RCC. Тут адреса зашита в тип: переплутати регістри
// не вийде навіть випадково, а весь доступ лишається одним записом
// у пам'ять — жодного зайвого коду проти макроса не породжується.
#pragma once

#include <cstdint>

namespace hw {

template <std::uintptr_t Address>
class Register {
public:
    static volatile std::uint32_t& raw() noexcept
    {
        return *reinterpret_cast<volatile std::uint32_t*>(Address);
    }

    [[nodiscard]] static std::uint32_t read() noexcept { return raw(); }
    static void write(std::uint32_t value) noexcept { raw() = value; }
    static void set(std::uint32_t mask) noexcept { raw() = raw() | mask; }
    static void clear(std::uint32_t mask) noexcept { raw() = raw() & ~mask; }

    static void modify(std::uint32_t clear_mask, std::uint32_t set_mask) noexcept
    {
        raw() = (raw() & ~clear_mask) | set_mask;
    }

    [[nodiscard]] static bool any(std::uint32_t mask) noexcept
    {
        return (raw() & mask) != 0U;
    }
};

// Іменоване бітове поле. Ширина й позиція перевіряються на етапі
// компіляції, тож «сусіднє поле, зсунуте на біт» неможливе за побудовою.
template <unsigned Pos, unsigned Width>
struct Field {
    static_assert(Width > 0 && Pos + Width <= 32, "поле не вміщається в регістр");

    static constexpr std::uint32_t mask =
        ((Width == 32U) ? ~0U : ((1U << Width) - 1U)) << Pos;

    [[nodiscard]] static constexpr std::uint32_t of(std::uint32_t value) noexcept
    {
        return (value << Pos) & mask;
    }
};

inline void dsb() noexcept { __asm volatile("dsb 0xF" ::: "memory"); }
inline void isb() noexcept { __asm volatile("isb 0xF" ::: "memory"); }
inline void disable_irq() noexcept { __asm volatile("cpsid i" ::: "memory"); }

[[nodiscard]] inline std::uint32_t main_stack_pointer() noexcept
{
    std::uint32_t sp{};
    __asm volatile("mrs %0, msp" : "=r"(sp));
    return sp;
}

} // namespace hw
