/* ============================================================================
   krok-2-emergency-nvs-flush.c — ESP-IDF: аварійне збереження в NVS (Dying Gasp)
   ========================================================================== */

#include <stdio.h>
#include "esp_log.h"
#include "esp_timer.h"
#include "driver/gpio.h"
#include "nvs_flash.h"
#include "nvs.h"
#include "esp_wifi.h"

static const char *TAG = "EMERGENCY_FLUSH";

#define GPIO_RELAY_CTRL    GPIO_NUM_18

typedef struct {
    uint32_t switch_cycles;
    uint32_t last_energy_wh;
    uint8_t  last_state;
} device_state_t;

static nvs_handle_t s_nvs_handle;

void emergency_nvs_init(void) {
    esp_err_t err = nvs_flash_init();
    if (err == ESP_ERR_NVS_NO_FREE_PAGES || err == ESP_ERR_NVS_NEW_VERSION_FOUND) {
        ESP_ERROR_CHECK(nvs_flash_erase());
        err = nvs_flash_init();
    }
    ESP_ERROR_CHECK(err);
    ESP_ERROR_CHECK(nvs_open("mains_state", NVS_READWRITE, &s_nvs_handle));

    gpio_set_direction(GPIO_RELAY_CTRL, GPIO_MODE_OUTPUT);
}

// Функція викликається негайно при виявленні втрати мережі 220 В
// Доступне вікно живлення від вихідної ємності HLK-PM: ~20..30 мс
void emergency_dying_gasp(const device_state_t *state) {
    int64_t t_start = esp_timer_get_time();

    // 1. Негайне зняття навантаження: відключаємо котушку реле (економія 60-80 мА)
    gpio_set_level(GPIO_RELAY_CTRL, 0);

    // 2. Вимикаємо Wi-Fi передавач (струм падає з 180 мА до ~20 мА)
    // Це подовжує час утримання вихідної напруги HLK-PM у 3-4 рази!
    esp_wifi_stop();

    // 3. Запис критичного стану в енергонезалежну пам'ять NVS
    nvs_set_u32(s_nvs_handle, "cycles", state->switch_cycles);
    nvs_set_u32(s_nvs_handle, "energy", state->last_energy_wh);
    nvs_set_u8(s_nvs_handle, "state", state->last_state);
    nvs_commit(s_nvs_handle);

    int64_t elapsed_us = esp_timer_get_time() - t_start;
    ESP_LOGW(TAG, "Аварійне збереження виконано за %lld мкс! Вхід в очікування вимкнення.", elapsed_us);

    // Засинаємо, щоб уникнути хаотичних перезавантажень при brownout
    while (1) {
        vTaskDelay(pdMS_TO_TICKS(100));
    }
}
