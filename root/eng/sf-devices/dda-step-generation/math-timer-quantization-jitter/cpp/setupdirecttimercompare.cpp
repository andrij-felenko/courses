// Реалізація подвійного буферування періоду таймера для апаратного виводу
#include <Arduino.h>

void setupDirectTimerCompare() {
    pinMode(9, OUTPUT); // Вивід OC1A для апаратного тогглінгу
    
    // Скидання налаштувань Timer1
    TCCR1A = 0;
    TCCR1B = 0;
    TCNT1  = 0;

    // Режим CTC (Clear Timer on Compare) з апаратним тогглінгом виводу OC1A
    TCCR1A |= (1 << COM1A0); 
    TCCR1B |= (1 << WGM12) | (1 << CS10); // Prescaler = 1 (f_timer = f_CPU)

    // Запис першого періоду в буферизований регістр OCR1A
    OCR1A = 1599; // 16 MHz / (10 kHz * 1) - 1
}

void loadNextDDAPeriod(uint16_t next_ticks) {
    // Запис нового значення відбувається в тільовий буферний регістр
    // Оновлення фізичного регістру відбудеться апаратно в момент збігу
    OCR1A = next_ticks;
}
