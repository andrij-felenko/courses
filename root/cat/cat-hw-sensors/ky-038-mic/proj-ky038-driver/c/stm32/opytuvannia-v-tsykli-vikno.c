static uint32_t last_event  = 0;   // HAL_GetTick() останньої зарахованої події
static uint32_t sound_count = 0;   // лічильник гучних подій
#define WINDOW_MS  300             // мертва зона після події

void ky038_poll(void) {            // кличемо щоразу з головного while (1)
    static uint8_t was_sound = 0;                  // чи був звук у попередній ітерації
    uint8_t is_sound = (HAL_GPIO_ReadPin(DO_PORT, DO_PIN) != idle_level);

    // цікавить саме ФРОНТ: тиша щойно змінилася на звук
    if (is_sound && !was_sound) {
        uint32_t now = HAL_GetTick();              // мілісекунди від старту, 32 біти
        if (now - last_event > WINDOW_MS) {        // і вікно вже минуло
            last_event = now;
            sound_count++;
            printf("подія #%lu\r\n", (unsigned long)sound_count);
        }
    }
    was_sound = is_sound;

    // ... решта while (1) вільна робити будь-що, бо ми ніде не чекаємо ...
}
