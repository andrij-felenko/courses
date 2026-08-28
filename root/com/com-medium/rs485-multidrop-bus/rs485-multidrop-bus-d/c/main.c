// ============================================================================
// Мова C: Коректний алгоритм відправки кадру по RS-485 з перевіркою прапорця TC
// ============================================================================
#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

extern void gpio_set_de_pin(bool state);
extern bool uart_is_txe(void);
extern bool uart_is_tc(void);
extern void uart_send_byte_raw(uint8_t b);

void rs485_send_buffer(const uint8_t *data, size_t len) {
    // 1. Переводимо трансивер у режим передачі
    gpio_set_de_pin(true);

    for (size_t i = 0; i < len; i++) {
        // Очікуємо готовності апаратного буфера передачі (TXE)
        while (!uart_is_txe());
        uart_send_byte_raw(data[i]);
    }

    // 2. Обов'язково чекаємо повного виходу останнього стоп-біта у дріт (TC!)
    while (!uart_is_tc());

    // 3. Звільняємо шину — повертаємося в режим приймання High-Z
    gpio_set_de_pin(false);
}
