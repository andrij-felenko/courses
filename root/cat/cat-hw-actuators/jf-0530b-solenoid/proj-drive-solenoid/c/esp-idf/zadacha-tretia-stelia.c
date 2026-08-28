#include "esp_log.h"

#define SOL_PIN    GPIO_NUM_5
#define MAX_ON_MS  3000              // ГРАНИЦЯ: довше 3 с під струмом не тримаємо НІКОЛИ
static const char *TAG = "solenoid";

static bool     sol_on    = false;
static uint32_t sol_start = 0;

void solenoid_on(void) {             // «тримати ввімкненим» (напр. утримувати засувку)
    if (!sol_on) {                   // фіксуємо мить старту лише на першому вмиканні
        gpio_set_level(SOL_PIN, 1);
        sol_start = now_ms();
        sol_on    = true;
    }
}

void solenoid_off(void) {
    gpio_set_level(SOL_PIN, 0);
    sol_on = false;
}

void solenoid_update(void) {         // страхувальник: рубає струм, якщо тримають задовго
    if (sol_on && (now_ms() - sol_start >= MAX_ON_MS)) {
        solenoid_off();              // стеля вичерпана — гасимо примусово
        ESP_LOGE(TAG, "утримання > %d мс — примусове вимкнення", MAX_ON_MS);
        // хтось тримає соленоїд надто довго — це майже завжди баг логіки
    }
}
