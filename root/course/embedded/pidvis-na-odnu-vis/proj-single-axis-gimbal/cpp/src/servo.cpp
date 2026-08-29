#include "servo.hpp"

#include <avr/io.h>

namespace gimbal {

void RcServo::begin() noexcept {
    DDRB |= (1 << PB1);  // OC1A на вихід

    // Спершу нейтраль, щоб перший же кадр не кинув вал в упор.
    OCR1A = static_cast<std::uint16_t>(kMid.value * kTicksPerUs - 1);
    ICR1  = static_cast<std::uint16_t>(kFrameUs * kTicksPerUs - 1);

    // Режим 14: Fast PWM, вершина в ICR1, неінвертований вихід OC1A.
    TCCR1A = (1 << COM1A1) | (1 << WGM11);
    TCCR1B = (1 << WGM13) | (1 << WGM12) | (1 << CS11);
}

void RcServo::write(Microseconds pulse) noexcept {
    const std::uint16_t us = std::clamp(pulse.value, kMin.value, kMax.value);

    // OCR1A подвійно буферизований: запис підхоплюється на межі кадру,
    // тож укорочений імпульс не з'явиться навіть при записі всередині кадру.
    OCR1A = static_cast<std::uint16_t>(us * kTicksPerUs - 1);
}

}  // namespace gimbal
