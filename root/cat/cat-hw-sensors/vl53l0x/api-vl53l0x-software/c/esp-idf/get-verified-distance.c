#include "vl53l0x_api.h"
#include "esp_log.h"

static const char *TAG = "VL53L0X_DIAG";

// Захисна функція зчитування з перевіркою кодів помилок та статусів якості
bool get_verified_distance(VL53L0X_Dev_t *p_device, uint16_t *out_distance_mm) {
    VL53L0X_RangingMeasurementData_t measure_data;
    VL53L0X_Error status = VL53L0X_GetRangingMeasurementData(p_device, &measure_data);

    // 1. Перевірка шини I2C та статусу API
    if (status != VL53L0X_ERROR_NONE) {
        ESP_LOGE(TAG, "Помилка I2C або API: %d", status);
        return false;
    }

    // 2. Перевірка апаратного статусу вимірювання RangeStatus
    if (measure_data.RangeStatus != 0) {
        ESP_LOGW(TAG, "Недостовірний замір, RangeStatus = %d", measure_data.RangeStatus);
        return false;
    }

    // 3. Дані валідні
    *out_distance_mm = measure_data.RangeMilliMeter;
    return true;
}
