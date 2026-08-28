// ─── hal_esp32.cpp ─────────────────────────────────────────────────────────
#if defined(ARDUINO_ARCH_ESP32)

#include "hal.h"
#include <Arduino.h>   // лише тут, не в прикладному коді

void hal_gpio_write(uint8_t pin, bool on) {
    digitalWrite(pin, on ? HIGH : LOW);
}

void hal_uart_puts(const char* s) {
    Serial.print(s);
}

void hal_delay_ms(uint32_t ms) {
    delay(ms);
}

uint32_t hal_millis(void) {
    return millis();
}

#endif // ARDUINO_ARCH_ESP32


// ─── hal_avr.cpp ───────────────────────────────────────────────────────────
// «Голий» AVR — не Arduino, прямий регістровий доступ до портів.
// Для стислості показана лише hal_gpio_write; решта — аналогічно.
#if defined(__AVR__)

#include "hal.h"
#include <avr/io.h>
#include <util/delay.h>
extern volatile uint32_t timer0_millis;  // з вбудованого ISR таймера

// УВАГА: hal_init() мусить виконати DDRB |= (1<<pin), щоб пін був виходом.
void hal_gpio_write(uint8_t pin, bool on) {
    if (on)  PORTB |=  (1 << pin);  // встановити біт
    else     PORTB &= ~(1 << pin);  // скинути біт
}

void hal_uart_puts(const char* s) {
    while (*s) {
        while (!(UCSR0A & (1 << UDRE0)));  // чекати, поки буфер вільний
        UDR0 = (uint8_t)(*s++);
    }
}

void hal_delay_ms(uint32_t ms) {
    while (ms--) _delay_ms(1);
}

uint32_t hal_millis(void) {
    return timer0_millis;
}

#endif // __AVR__


// ─── hal_stm32.cpp ─────────────────────────────────────────────────────────
#if defined(ARDUINO_ARCH_STM32)

#include "hal.h"
#include <Arduino.h>

void hal_gpio_write(uint8_t pin, bool on) {
    digitalWrite(pin, on ? HIGH : LOW);
}

void hal_uart_puts(const char* s) {
    Serial.print(s);
}

void hal_delay_ms(uint32_t ms) {
    delay(ms);
}

uint32_t hal_millis(void) {
    return millis();
}

#endif // ARDUINO_ARCH_STM32


// ─── #else: не допустити тихої збірки для непідтримуваного чипа ─────────────
#if !defined(ARDUINO_ARCH_ESP32) && !defined(__AVR__) && !defined(ARDUINO_ARCH_STM32)
  #error "hal: невідома цільова платформа — реалізуйте HAL для цього чипа!"
#endif
