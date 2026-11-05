#include <Wire.h>
#include <VL53L0X.h>

VL53L0X sensor;

// Структура для зберігання калібрування в EEPROM
struct CalibrationData {
    uint32_t magic;
    float crosstalkRate;
    int16_t offsetMicrometers;
};

void applyStoredCalibration(VL53L0X &dev, const CalibrationData &calib) {
    // Застосовуємо збережені параметри crosstalk та offset під час старту
    dev.setXtalkRate(calib.crosstalkRate);
    dev.setOffset(calib.offsetMicrometers);
}
