#pragma once

#include <cstdint>

/*
 * Вивід тактового сигналу на пін PA8 (MCO1) для перевірки осцилографом.
 * Щуп на OSC_IN/OSC_OUT зриває генерацію — міряють саме тут.
 */

namespace bsp::mco {

enum class Source : std::uint32_t {
    hsi = 0b00,
    lse = 0b01,
    hse = 0b10,
    pll = 0b11
};

enum class Prescaler : std::uint32_t {
    div1 = 0b000,
    div2 = 0b100,
    div3 = 0b101,
    div4 = 0b110,
    div5 = 0b111
};

/* Налаштувати PA8 на вихід MCO1 із заданим джерелом і дільником */
void enable_on_pa8(Source source, Prescaler prescaler) noexcept;

/* Скільки має показати осцилограф при поточному SYSCLK і цьому дільнику */
std::uint32_t expected_hz(Prescaler prescaler) noexcept;

} // namespace bsp::mco
