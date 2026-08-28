#include <avr/sleep.h>
#include <avr/wdt.h>
#include <avr/interrupt.h>

// прокидання від сторожового таймера — обробник має бути, хай і порожній
ISR(WDT_vect) { /* просто будить чип */ }

void setup() {
    // налаштувати watchdog на переривання (не скид) кожні ~8 с
    cli();                                  // заборонити переривання на час зміни
    wdt_reset();
    WDTCSR = (1 << WDCE) | (1 << WDE);      // відкрити зміну
    WDTCSR = (1 << WDIE) | (1 << WDP3) | (1 << WDP0);  // WDIE=переривання, ~8 с
    sei();                                  // дозволити переривання назад
}

void loop() {
    // 1. корисна робота (тут — блимнути, а реально: виміряти й записати)
    digitalWrite(LED_BUILTIN, HIGH); delay(20); digitalWrite(LED_BUILTIN, LOW);

    // 2. заснути найглибше до наступного «цок» watchdog
    set_sleep_mode(SLEEP_MODE_PWR_DOWN);
    sleep_enable();
    sleep_cpu();          // ← тут ядро зупиняється; прокинеться в ISR(WDT_vect)
    sleep_disable();      // виконається вже після пробудження
}
