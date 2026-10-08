// Приклад неблокуючого драйвера фонового сканування (ESP-IDF / C)
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
#include "freertos/FreeRTOS.h"
#include "freertos/portmacro.h"

#define NUM_DIGITS 4

static uint8_t raw_buffer_a[NUM_DIGITS];
static uint8_t raw_buffer_b[NUM_DIGITS];

static uint8_t* volatile front_buffer = raw_buffer_a;
static uint8_t* volatile back_buffer = raw_buffer_b;
static volatile uint8_t current_digit = 0;

// Апаратне переривання таймера (викликається з частотою 400 Гц)
void IRAM_ATTR display_timer_isr(void* arg) {
    // 1. Інтервал гасіння: вимикаємо всі розрядні ключі
    disable_all_digits();

    // 2. Виставити сегментний код з активного буфера (front_buffer)
    uint8_t mask = front_buffer[current_digit];
    set_segment_bus(mask);

    // 3. Увімкнути ключ поточного розряду
    enable_digit(current_digit);

    // 4. Перехід до наступного розряду
    current_digit = (current_digit + 1) % NUM_DIGITS;
}

// Потік головної програми: оновлення даних на екрані
void display_update_frame(const uint8_t* new_masks) {
    // Запис у фоновий буфер без зачіпання активного сканування
    memcpy((void*)back_buffer, new_masks, NUM_DIGITS);

    // Атомарна підміна вказівників буферів
    taskENTER_CRITICAL_ISR();
    uint8_t* temp = front_buffer;
    front_buffer = back_buffer;
    back_buffer = temp;
    taskEXIT_CRITICAL_ISR();
}
