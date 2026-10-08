#include <VL53L0X.h>

extern VL53L0X sensor;

// Неблокуюче зчитування відстані
bool getDistanceIfReady(uint16_t &distance_mm) {
    // Перевірка наявності нового значення
    if (sensor.timeoutOccurred()) {
        return false;
    }
    
    // Зчитування виміряного значення в міліметрах
    distance_mm = sensor.readRangeContinuousMillimeters();
    return true;
}
