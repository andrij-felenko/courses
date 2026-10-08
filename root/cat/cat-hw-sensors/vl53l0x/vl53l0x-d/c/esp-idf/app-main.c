#include <stdio.h>
#include "freertos/FreeRTOS.h"
#include "freertos/task.h"
#include "vl53l0x_api.h"

void app_main(void) {
    VL53L0X_Dev_t dev;
    VL53L0X_Error status;

    // Ініціалізація структури пристрою та базової адреси I2C
    dev.I2cDevAddr = 0x29;
    status = VL53L0X_DataInit(&dev);

    if (status == VL53L0X_ERROR_NONE) {
        status = VL53L0X_StaticInit(&dev);
    }

    // Налаштування часового бюджету вимірювання на 200 мс
    if (status == VL53L0X_ERROR_NONE) {
        status = VL53L0X_SetMeasurementTimingBudgetMicroSeconds(&dev, 200000);
    }

    // Встановлення режимів безперервного вимірювання
    if (status == VL53L0X_ERROR_NONE) {
        status = VL53L0X_SetDeviceMode(&dev, VL53L0X_DEVICEMODE_CONTINUOUS_RANGING);
    }

    // Запуск лазерного випромінювача та обробки SPAD
    if (status == VL53L0X_ERROR_NONE) {
        status = VL53L0X_StartMeasurement(&dev);
    }

    VL53L0X_RangingMeasurementData_t data;
    while (1) {
        status = VL53L0X_GetRangingMeasurementData(&dev, &data);
        if (status == VL53L0X_ERROR_NONE && data.RangeStatus == 0) {
            printf("Виміряна відстань: %u мм\n", data.RangeMilliMeter);
        }
        VL53L0X_ClearInterruptMask(&dev, 0);
        vTaskDelay(pdMS_TO_TICKS(200));
    }
}
