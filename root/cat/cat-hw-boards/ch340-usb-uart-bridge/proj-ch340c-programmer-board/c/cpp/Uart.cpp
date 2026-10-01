#include "Uart.hpp"
#include <avr/io.h>

#ifndef F_CPU
#define F_CPU 16000000UL
#endif

Uart::Uart(uint32_t baud_rate) {
    init(baud_rate);
}

Uart::~Uart() {
    /* Вимкнення приймача та передавача при знищенні об'єкта (RAII) */
    UCSR0B = 0;
}

void Uart::init(uint32_t baud_rate) noexcept {
    const uint16_t ubrr_value = static_cast<uint16_t>((F_CPU / (16UL * baud_rate)) - 1);

    /* Встановлення швидкості обміну у регістри UBRR */
    UBRR0H = static_cast<uint8_t>(ubrr_value >> 8);
    UBRR0L = static_cast<uint8_t>(ubrr_value);

    /* Активація блоків передачі та прийому UART */
    UCSR0B = (1 << RXEN0) | (1 << TXEN0);

    /* Формат кадру: 8 біт даних, 1 стоп-біт (8N1) */
    UCSR0C = (1 << UCSZ01) | (1 << UCSZ00);
}

bool Uart::is_data_available() const noexcept {
    return (UCSR0A & (1 << RXC0)) != 0;
}

uint8_t Uart::receive_byte() const noexcept {
    while (!is_data_available()) {
        /* Блокуючий цикл очікування даних від CH340 */
    }
    return UDR0;
}

bool Uart::receive_byte_nonblocking(uint8_t& out_data) const noexcept {
    if (!is_data_available()) {
        return false;
    }
    out_data = UDR0;
    return true;
}

void Uart::send_byte(uint8_t data) const noexcept {
    while (!(UCSR0A & (1 << UDRE0))) {
        /* Очікування звільнення регістру даних передавача */
    }
    UDR0 = data;
}

void Uart::send_string(std::string_view str) const noexcept {
    for (char ch : str) {
        send_byte(static_cast<uint8_t>(ch));
    }
}
