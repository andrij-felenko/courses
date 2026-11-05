#include <stdint.h>
#include <stdbool.h>

// Структура мажоритарного фільтра GPIO
typedef struct {
    uint8_t history;       // Буфер 8 останніх вибірок стану піна
    bool debounced_state;  // Підтверджений стабільний стан лінії
} gpio_majority_filter_t;

void gpio_filter_init(gpio_majority_filter_t *filter, bool initial_state) {
    filter->history = initial_state ? 0xFF : 0x00;
    filter->debounced_state = initial_state;
}

// Функція викликається регулярним перериванням таймера з періодом t_sample
bool gpio_filter_update(gpio_majority_filter_t *filter, bool raw_pin_state) {
    // Зсув історії вліво та додавання нового відліку в молодший біт
    filter->history = (filter->history << 1) | (raw_pin_state ? 1 : 0);
    
    // Підрахунок кількості одиниць у 8-бітному буфері
    uint8_t ones_count = 0;
    for (uint8_t i = 0; i < 8; i++) {
        if ((filter->history >> i) & 0x01) {
            ones_count++;
        }
    }
    
    // Мажоритарний поріг: 6 або більше одиниць встановлюють HIGH, 2 або менше — LOW
    if (ones_count >= 6) {
        filter->debounced_state = true;
    } else if (ones_count <= 2) {
        filter->debounced_state = false;
    }
    
    return filter->debounced_state;
}
