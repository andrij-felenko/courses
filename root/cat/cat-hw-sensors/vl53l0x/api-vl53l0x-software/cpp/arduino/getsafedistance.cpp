#include <VL53L0X.h>

extern VL53L0X sensor;

// Отримання перевіреного значення відстані
bool getSafeDistance(uint16_t &valid_distance) {
    uint16_t dist = sensor.readRangeContinuousMillimeters();
    
    // Перевірка апаратного таймауту I2C
    if (sensor.timeoutOccurred()) {
        // Помилка зв'язку з пристроєм
        return false;
    }

    // В ардуїно-обгортці перевищення діапазону повертає 65535
    if (dist > 2000 || dist == 65535) {
        // Об'єкт поза межами вимірювання
        return false;
    }

    valid_distance = dist;
    return true;
}
