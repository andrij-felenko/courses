// Приклад неблокуючого обробника переривання таймера (ESP-IDF / C)
#include <stdint.h>
#include <stdbool.h>

#define NUM_DIGITS 4

static uint8_t display_buffer[NUM_DIGITS]; // Буфер відображення
static volatile uint8_t current_digit = 0;

void IRAM_ATTR display_scan_isr(void* arg) {
    // 1. Інтервал гасіння: вимикаємо всі розрядні ключі
    disable_all_digit_keys();

    // 2. Оновлюємо сегментну шину даними з буфера для поточного розряду
    uint8_t segment_mask = display_buffer[current_digit];
    set_segment_bus_mask(segment_mask);

    // 3. Вмикаємо ключ поточного розряду
    enable_digit_key(current_digit);

    // 4. Переходимо до наступного розряду для наступного переривання
    current_digit = (current_digit + 1) % NUM_DIGITS;
}
