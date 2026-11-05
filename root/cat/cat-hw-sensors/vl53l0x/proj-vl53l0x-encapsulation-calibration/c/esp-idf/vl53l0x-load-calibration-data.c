#include <stdio.h>
#include "driver/i2c.h"
#include "vl53l0x_api.h"

// Функція завантаження калібрувальних коефіцієнтів у регістри давача
esp_err_t vl53l0x_load_calibration_data(VL53L0X_DEV dev, FixPoint1616_t crosstalk_rate, int16_t offset_um) {
    VL53L0X_Error status = VL53L0X_ERROR_NONE;

    // Встановлюємо значення перехресного наведення в мікросхему
    status = VL53L0X_SetXtalkCompensationRateMegaCps(dev, crosstalk_rate);
    if (status != VL53L0X_ERROR_NONE) {
        return ESP_FAIL;
    }

    // Встановлюємо калібрувальний зсув відстані
    status = VL53L0X_SetMeasurementOffsetMicroMeter(dev, offset_um);
    if (status != VL53L0X_ERROR_NONE) {
        return ESP_FAIL;
    }

    return ESP_OK;
}
