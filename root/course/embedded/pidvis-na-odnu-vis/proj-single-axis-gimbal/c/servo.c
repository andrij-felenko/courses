#include "servo.h"

#include <avr/io.h>

#define SERVO_TICKS_PER_US 2u      /* 16 МГц / 8 = 2 такти на мікросекунду */
#define SERVO_FRAME_US     20000u  /* 50 Гц — стандартний кадр RC-серво */

#define SERVO_MIN_US 1000u
#define SERVO_MAX_US 2000u

void servo_init(void)
{
    DDRB |= (1 << PB1);   /* OC1A на вихід */

    /* Спершу нейтраль, щоб перший же кадр не кинув вал в упор. */
    OCR1A = (uint16_t)(1500u * SERVO_TICKS_PER_US) - 1u;
    ICR1  = (uint16_t)(SERVO_FRAME_US * SERVO_TICKS_PER_US) - 1u;

    /* Режим 14: Fast PWM, TOP = ICR1, неінвертований вихід на OC1A. */
    TCCR1A = (1 << COM1A1) | (1 << WGM11);
    TCCR1B = (1 << WGM13) | (1 << WGM12) | (1 << CS11);
}

void servo_write_us(uint16_t pulse_us)
{
    if (pulse_us < SERVO_MIN_US) pulse_us = SERVO_MIN_US;
    if (pulse_us > SERVO_MAX_US) pulse_us = SERVO_MAX_US;

    /* OCR1A подвійно буферизований: запис підхоплюється на межі кадру,
     * тож укорочений або подовжений імпульс не з'явиться навіть тоді,
     * коли ми пишемо в середині поточного. */
    OCR1A = (uint16_t)(pulse_us * SERVO_TICKS_PER_US) - 1u;
}
