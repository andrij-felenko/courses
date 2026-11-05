#include <stdint.h>
#include <stdbool.h>

#define INPUT_CHANNELS 32
#define CHIP_COUNT (INPUT_CHANNELS / 8)

typedef struct {
    uint8_t history[INPUT_CHANNELS];  // Вікно 8 останніх вибірок для кожного входу
    uint32_t debounced_state;         // Фільтрований поточний стан 32 входів
    uint32_t previous_state;          // Попередній фільтрований стан
    uint32_t pressed_events;          // Прапорці подій натискання (Rising Edge)
    uint32_t released_events;         // Прапорці подій відпускання (Falling Edge)
} debounce_manager_t;

void debounce_init(debounce_manager_t *mgr) {
    for (int i = 0; i < INPUT_CHANNELS; i++) {
        mgr->history[i] = 0xFF; // За замовчуванням підтяжка до VCC (не натиснуто)
    }
    mgr->debounced_state = 0xFFFFFFFF;
    mgr->previous_state = 0xFFFFFFFF;
    mgr->pressed_events = 0;
    mgr->released_events = 0;
}

// Оновлення фільтра новим сирим масивом байтів із 74HC165
void debounce_update(debounce_manager_t *mgr, const uint8_t *raw_bytes) {
    uint32_t current_filtered = 0;

    for (size_t channel = 0; channel < INPUT_CHANNELS; channel++) {
        size_t byte_idx = channel / 8;
        size_t bit_idx = channel % 8;
        bool raw_bit = (raw_bytes[byte_idx] & (1U << bit_idx)) != 0;

        // Зсув історії вліво та додавання нового біта
        mgr->history[channel] = (mgr->history[channel] << 1) | (raw_bit ? 1 : 0);

        // Фільтрація по зсувному вікну: 0xFF -> 1, 0x00 -> 0, інакше зберігаємо попередній стан
        if (mgr->history[channel] == 0xFF) {
            current_filtered |= (1U << channel);
        } else if (mgr->history[channel] == 0x00) {
            // Біт залишається 0
        } else {
            // Проміжний стан (дребезг): зберігаємо поточне фільтроване значення біта
            if (mgr->debounced_state & (1U << channel)) {
                current_filtered |= (1U << channel);
            }
        }
    }

    // Обчислення фронтів подій (при активному низькому рівні кнопок)
    // Натискання: перехід 1 -> 0 у фільтрованому стані
    mgr->pressed_events = (mgr->previous_state) & (~current_filtered);
    // Відпускання: перехід 0 -> 1 у фільтрованому стані
    mgr->released_events = (~mgr->previous_state) & (current_filtered);

    mgr->previous_state = mgr->debounced_state;
    mgr->debounced_state = current_filtered;
}

// Перевірка події натискання для конкретного входу
bool is_button_pressed_event(const debounce_manager_t *mgr, uint8_t channel) {
    if (channel >= INPUT_CHANNELS) return false;
    return (mgr->pressed_events & (1U << channel)) != 0;
}
