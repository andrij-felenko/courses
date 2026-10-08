#include <avr/io.h>

void timer1_servo_init(void) {
    // Налаштування виводу PB1 (OC1A / Pin 9) на вихід
    DDRB |= (1 << DDB1);

    // Скидання регістрів конфігурації
    TCCR1A = 0;
    TCCR1B = 0;

    // Режим Fast PWM з межею лічильника в ICR1 (Mode 14)
    // Non-inverting PWM на виводі OC1A
    TCCR1A |= (1 << COM1A1) | (1 << WGM11);
    TCCR1B |= (1 << WGM13) | (1 << WGM12);

    // Встановлення дільника частоти N = 8 (CS11 = 1)
    TCCR1B |= (1 << CS11);

    // Встановлення періоду 20 мс (50 Гц): ICR1 = 39999
    ICR1 = 39999;

    // Встановлення початкового імпульсу 1500 мкс (OCR1A = 3000)
    OCR1A = 3000;
}

void set_servo_pulse_us(uint16_t pulse_us) {
    // Кожен такт дорівнює 0.5 мкс, тому OCR1A = pulse_us * 2
    OCR1A = pulse_us * 2;
}
