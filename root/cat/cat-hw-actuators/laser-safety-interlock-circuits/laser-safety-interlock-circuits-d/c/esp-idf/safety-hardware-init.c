#include <stdio.h>
#include <stdbool.h>
#include "driver/gpio.h"
#include "esp_log.h"

#define PIN_INTERLOCK_FB   GPIO_NUM_4   // Вхід моніторингу оптопари (низький = безпечно)
#define PIN_EDM_FB         GPIO_NUM_5   // Вхід зворотності реле EDM (високий = контакти розімкнені)
#define PIN_MCU_ENABLE     GPIO_NUM_18  // Вихід апаратного стробування на логічний вентиль
#define PIN_RESET_BTN      GPIO_NUM_19  // Вхід кнопки скидання помилки

static const char *TAG = "LASER_SAFETY";

typedef enum {
    SAFETY_STATE_FAULT = 0,
    SAFETY_STATE_DISABLED,
    SAFETY_STATE_READY,
    SAFETY_STATE_ACTIVE
} safety_state_t;

static safety_state_t current_state = SAFETY_STATE_DISABLED;

void safety_hardware_init(void) {
    gpio_config_t io_conf = {
        .pin_bit_mask = (1ULL << PIN_INTERLOCK_FB) | (1ULL << PIN_EDM_FB) | (1ULL << PIN_RESET_BTN),
        .mode = GPIO_MODE_INPUT,
        .pull_up_en = GPIO_PULLUP_ENABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&io_conf);

    gpio_config_t out_conf = {
        .pin_bit_mask = (1ULL << PIN_MCU_ENABLE),
        .mode = GPIO_MODE_OUTPUT,
        .pull_up_en = GPIO_PULLUP_DISABLE,
        .pull_down_en = GPIO_PULLDOWN_DISABLE,
        .intr_type = GPIO_INTR_DISABLE
    };
    gpio_config(&out_conf);
    
    // Апаратне стробування початково заблоковане
    gpio_set_level(PIN_MCU_ENABLE, 0);
}

void safety_task_process(void) {
    bool interlock_ok = (gpio_get_level(PIN_INTERLOCK_FB) == 0);
    bool edm_ok       = (gpio_get_level(PIN_EDM_FB) == 1);
    bool reset_pressed = (gpio_get_level(PIN_RESET_BTN) == 0);

    switch (current_state) {
        case SAFETY_STATE_DISABLED:
            gpio_set_level(PIN_MCU_ENABLE, 0);
            if (interlock_ok && edm_ok) {
                current_state = SAFETY_STATE_READY;
                ESP_LOGI(TAG, "Контур безпеки замкнено. Готовий до скидання.");
            }
            break;

        case SAFETY_STATE_READY:
            if (!interlock_ok) {
                current_state = SAFETY_STATE_DISABLED;
            } else if (reset_pressed) {
                current_state = SAFETY_STATE_ACTIVE;
                gpio_set_level(PIN_MCU_ENABLE, 1);
                ESP_LOGI(TAG, "Дозвіл на випромінювання видано.");
            }
            break;

        case SAFETY_STATE_ACTIVE:
            // Якщо силова схема розімкнулася, апаратний І-вентиль вже відключив лазер.
            // Мікроконтролер синхронізує свій стан та знімає свій сигнал Enable.
            if (!interlock_ok) {
                gpio_set_level(PIN_MCU_ENABLE, 0);
                current_state = SAFETY_STATE_DISABLED;
                ESP_LOGW(TAG, "Спрацював апаратний інтерлок! Випромінювання заблоковано.");
            }
            break;

        case SAFETY_STATE_FAULT:
        default:
            gpio_set_level(PIN_MCU_ENABLE, 0);
            ESP_LOGE(TAG, "Критична апаратна відмова контуру безпеки.");
            break;
    }
}
