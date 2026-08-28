#include <stdint.h>
#include <stdbool.h>

typedef struct {
    uint8_t counter;       // Поточний лічильник стабільності вибірки
    uint8_t threshold;     // Поріг підтвердження стану (кількість відліків)
    bool stable_state;     // Відфільтрований стабільний стан контакту
} DebounceEngine;

void debounce_engine_init(DebounceEngine* eng, uint8_t filter_samples) {
    eng->counter = 0;
    eng->threshold = filter_samples;
    eng->stable_state = false;
}

// Викликається періодично з системного таймера (наприклад, системний тик SysTick 1 мс)
bool debounce_engine_process(DebounceEngine* eng, bool raw_input_pin) {
    if (raw_input_pin != eng->stable_state) {
        eng->counter++;
        if (eng->counter >= eng->threshold) {
            eng->stable_state = raw_input_pin;
            eng->counter = 0;
        }
    } else {
        eng->counter = 0; // Скидання лічильника при будь-якому випадковому коливанні
    }
    return eng->stable_state;
}
