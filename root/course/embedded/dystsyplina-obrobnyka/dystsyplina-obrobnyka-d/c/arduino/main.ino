/* Дисциплінований підхід для Arduino / AVR: Pin Change Interrupt */
#include <avr/interrupt.h>

volatile uint32_t pulse_count = 0;
volatile bool pulse_ready_flag = false;

/* Обробник зовнішнього переривання INT0 */
ISR(INT0_vect) {
    /* 1. Швидка дія: інкремент 32-бітного лічильника */
    pulse_count++;
    
    /* 2. Встановлення прапорця для головного циклу */
    pulse_ready_flag = true;
    
    /* Вихід: жодного Serial.print(), жодного delay()! */
}

void loop() {
    if (pulse_ready_flag) {
        uint32_t current_pulses;

        /* Читання 32-бітної змінної на 8-бітному ядрі AVR під критичною секцією */
        cli(); // Заборона переривань
        current_pulses = pulse_count;
        pulse_ready_flag = false;
        sei(); // Дозвіл переривань

        /* Форматований вивід виконується виключно в loop() */
        Serial.print("Impulses received: ");
        Serial.println(current_pulses);
    }
}
