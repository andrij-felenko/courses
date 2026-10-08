#include "esp_log.h"
#include "driver/gpio.h"
#include "driver/i2c.h"

static const char *TAG = "VL53L0X_DIAG";

typedef enum {
    RANGE_STATUS_OK = 0,
    RANGE_STATUS_SIGMA_FAIL = 1,
    RANGE_STATUS_SIGNAL_FAIL = 2,
    RANGE_STATUS_MIN_RANGE_FAIL = 3,
    RANGE_STATUS_OUT_OF_BOUNDS = 4
} vl53l0x_range_status_t;

void diagnose_ranging_result(uint8_t status_byte, uint16_t distance_mm) {
    uint8_t status = (status_byte >> 3) & 0x0F;
    
    switch (status) {
        case RANGE_STATUS_OK:
            ESP_LOGI(TAG, "Виміряна відстань: %d мм", distance_mm);
            break;
        case RANGE_STATUS_SIGMA_FAIL:
            ESP_LOGW(TAG, "Завада освітлення (Sigma Fail). Перевірте фонові клк!");
            break;
        case RANGE_STATUS_SIGNAL_FAIL:
            ESP_LOGW(TAG, "Низький рівень сигналу MCPS (Signal Fail). Перевірте альбедо цілі.");
            break;
        case RANGE_STATUS_MIN_RANGE_FAIL:
            ESP_LOGW(TAG, "Мертва зона (Min Range Fail). Об'єкт ближче за мінімальну межу.");
            break;
        default:
            ESP_LOGE(TAG, "Невідома відмова вимірювача. Код статусу: %d", status);
            break;
    }
}
