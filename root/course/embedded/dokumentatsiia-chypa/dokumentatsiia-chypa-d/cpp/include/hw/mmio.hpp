/* mmio.hpp — робота з відображеною в пам'ять периферією.
 *
 * Тут немає жодного макроса: адреси й бітові маски — constexpr-значення,
 * тож компілятор перевіряє їхні типи, а налагоджувач бачить імена.
 * Потрібен C++23 (std::expected в решті модулів), arm-none-eabi-gcc 13+.
 */
#pragma once

#include <cstdint>

namespace hw {

/* Частота як окреме ім'я типу: у сигнатурах видно, що передають герци,
 * а не «якесь число». */
using Hertz = std::uint32_t;

/* Накладає структуру регістрової карти на фізичну адресу. Посилання, а не
 * вказівник: блок периферії існує завжди й ніколи не буває нульовим. */
template <typename Block>
[[nodiscard]] inline Block& block(std::uintptr_t address) noexcept
{
    return *reinterpret_cast<Block*>(address);
}

[[nodiscard]] constexpr std::uint32_t bit(unsigned index) noexcept
{
    return std::uint32_t{1} << index;
}

[[nodiscard]] constexpr std::uint32_t mask(unsigned width, unsigned shift) noexcept
{
    return ((std::uint32_t{1} << width) - 1U) << shift;
}

/* Запис поля з кількох біт — єдине місце, де в цьому проєкті відбувається
 * read-modify-write. Для прапорців стану він заборонений (там W1C та rc_w0),
 * але конфігураційні поля R/W інакше не пишуться. */
inline void write_field(volatile std::uint32_t& reg,
                        unsigned shift,
                        unsigned width,
                        std::uint32_t value) noexcept
{
    const std::uint32_t m = mask(width, shift);
    std::uint32_t current = reg;
    current &= ~m;
    current |= (value << shift) & m;
    reg = current;
}

/* Бар'єри ядра (PM0214 §3.4): dsb дочікується завершення всіх звернень до
 * пам'яті, isb скидає конвеєр вибірки інструкцій. */
inline void dsb() noexcept { asm volatile("dsb 0xF" ::: "memory"); }
inline void isb() noexcept { asm volatile("isb 0xF" ::: "memory"); }
inline void nop() noexcept { asm volatile("nop"); }

} // namespace hw
