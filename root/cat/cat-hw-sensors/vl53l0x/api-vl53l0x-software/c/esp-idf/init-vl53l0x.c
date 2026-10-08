#include "vl53l0x_api.h"

// Ініціалізація давача VL53L0X через ST API
VL53L0X_Error init_vl53l0x(VL53L0X_Dev_t *p_device) {
    VL53L0X_Error status = VL53L0X_ERROR_NONE;
    uint32_t ref_spad_count;
    uint8_t is_aperture_spad;
    uint8_t vhv_settings;
    uint8_t phase_cal;

    // 1. Зчитування заводських даних та налаштування I2C
    status = VL53L0X_DataInit(p_device);
    if (status != VL53L0X_ERROR_NONE) return status;

    // 2. Статична конфігурація регістрів
    status = VL53L0X_StaticInit(p_device);
    if (status != VL53L0X_ERROR_NONE) return status;

    // 3. Калібрування масиву SPAD
    status = VL53L0X_PerformRefSpadManagement(p_device, &ref_spad_count, &is_aperture_spad);
    if (status != VL53L0X_ERROR_NONE) return status;

    // 4. Опорне калібрування напруги та фази
    status = VL53L0X_PerformRefCalibration(p_device, &vhv_settings, &phase_cal);
    return status;
}
