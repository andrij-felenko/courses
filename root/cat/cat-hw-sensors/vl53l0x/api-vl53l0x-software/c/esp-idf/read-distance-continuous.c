#include "vl53l0x_api.h"

// Безперервне зчитування відстані в міліметрах
VL53L0X_Error read_distance_continuous(VL53L0X_Dev_t *p_device, uint16_t *p_distance_mm) {
    VL53L0X_Error status = VL53L0X_ERROR_NONE;
    uint8_t data_ready = 0;
    VL53L0X_RangingMeasurementData_t measurement_data;

    // Перевірка готовності нових даних у буфері давача
    status = VL53L0X_GetMeasurementDataReady(p_device, &data_ready);
    if (status == VL53L0X_ERROR_NONE && data_ready == 1) {
        // Зчитування структури вимірювання
        status = VL53L0X_GetRangingMeasurementData(p_device, &measurement_data);
        if (status == VL53L0X_ERROR_NONE) {
            *p_distance_mm = measurement_data.RangeMilliMeter;
            // Очищення прапорця переривання для наступного заміру
            VL53L0X_ClearInterruptMask(p_device, VL53L0X_REG_SYSTEM_INTERRUPT_GPIO_NEW_SAMPLE_READY);
        }
    }
    return status;
}
