#include <stdint.h>
#include <stdbool.h>
#include "driver/gpio.h"
#include "freertos/FreeRTOS.h"
#include "freertos/queue.h"

// Структура опису події зміни стану вхідного контакту
typedef struct {
    uint8_t pin_index;        // Індекс зчитаного виводу (0-31)
    bool new_state;           // Новий підтверджений стан (true - HIGH, false - LOW)
    uint32_t timestamp_ms;    // Часова мітка підтвердження події
} button_event_t;

// Структура паралельного фільтра брязкіту для 32 ліній GPIO
typedef struct {
    uint32_t state;           // Поточний підтверджений стан 32 виводів
    uint32_t deb0;            // Молодший біт побітового лічильника стабільності
    uint32_t deb1;            // Старший біт побітового лічильника стабільності
    QueueHandle_t event_queue;// Черга RTOS для передачі подій
} parallel_debouncer_t;

// Ініціалізація паралельного фільтра
void parallel_debouncer_init(parallel_debouncer_t *db, uint32_t initial_state, QueueHandle_t queue) {
    db->state = initial_state;
    db->deb0 = 0xFFFFFFFFU;
    db->deb1 = 0xFFFFFFFFU;
    db->event_queue = queue;
}

// Функція опитування, що викликається з таймерного переривання ISR
void parallel_debouncer_update_from_isr(parallel_debouncer_t *db, uint32_t raw_sample, BaseType_t *higher_priority_task_woken) {
    // Обчислення бітів, які відрізняються від поточного підтвердженого стану
    uint32_t delta = raw_sample ^ db->state;

    // Оновлення двобітного побітового лічильника вертикального накопичення
    db->deb0 = db->deb0 ^ delta;
    db->deb1 = db->deb1 ^ (delta & ~db->deb0);

    // Маска виводів, рівень яких залишався стабільним протягом 4 послідовних тактів
    uint32_t changes = delta & ~db->deb0 & ~db->deb1;

    if (changes != 0U) {
        // Оновлення підтвердженого стану тільки для виводів, що змінили рівень
        db->state ^= changes;

        // Поітераційний розбір змінених бітів та відправка подій у чергу RTOS
        for (uint8_t i = 0; i < 32; i++) {
            if ((changes & (1U << i)) != 0U) {
                button_event_t evt = {
                    .pin_index = i,
                    .new_state = ((db->state & (1U << i)) != 0U),
                    .timestamp_ms = xTaskGetTickCountFromISR() * portTICK_PERIOD_MS
                };
                if (db->event_queue != NULL) {
                    xQueueSendFromISR(db->event_queue, &evt, higher_priority_task_woken);
                }
            }
        }
    }
}
