#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"

// Структура програмного дебаунсера на основі зсувного регістра
typedef struct {
    gpio_num_t gpio_num;       // Номер лінії GPIO
    uint8_t history;           // 8-бітний зсувний регістр історії рівнів
    bool debounced_state;      // Поточний підтверджений стан лінії
    bool last_stable_state;    // Попередній стабільний стан для виявлення фронту
} button_debounce_t;

// Ініціалізація модуля дебаунсера
void button_debounce_init(button_debounce_t *btn, gpio_num_t gpio_num) {
    btn->gpio_num = gpio_num;
    btn->history = 0xFF; // Початковий стан — підтягнуто до одиниці
    btn->debounced_state = true;
    btn->last_stable_state = true;

    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << gpio_num),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);
}

// Періодична функція опитування (викликається з переривання таймера або RTOS-задачі)
// Повертає true, якщо зафіксовано новий підтверджений фронт натискання (Falling Edge)
bool button_debounce_update(button_debounce_t *btn) {
    // Зчитуємо поточний логічний рівень безпосередньо з регістру IDR
    int raw_level = gpio_get_level(btn->gpio_num);

    // Зсуваємо історію вліво та додаємо новий біт у молодший розряд
    btn->history = (btn->history << 1) | (raw_level & 0x01);

    // Перевіряємо маску стабільності:
    // 0x00 відповідає 8 послідовним нуля (натиснуто)
    // 0xFF відповідає 8 послідовним одиницям (відпущено)
    if (btn->history == 0x00) {
        btn->debounced_state = false; // Логічний нуль підтверджено
    } else if (btn->history == 0xFF) {
        btn->debounced_state = true;  // Логічна одиниця підтверджена
    }
    // Проміжні значення історії означають триваючий брязкіт і ігноруються

    // Фіксуємо подійний фронт розмикання/замикання
    bool pressed_event = false;
    if (btn->last_stable_state && !btn->debounced_state) {
        pressed_event = true; // Зафіксовано спадаючий фронт (натискання)
    }
    btn->last_stable_state = btn->debounced_state;

    return pressed_event;
}
