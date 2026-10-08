#include <VL53L0X.h>

VL53L0X sensor;

// Обгортка ініціалізації C++ об'єкта давача
bool initVL53L0X() {
    // Налаштування I2C та базових параметрів
    sensor.setTimeout(500);
    if (!sensor.init()) {
        // Статична ініціалізація або калібрування повернули помилку
        return false;
    }
    
    // Переведення в стандартний режим із готовими параметрами SPAD
    sensor.setMeasurementTimingBudget(33000); // 33 мс
    return true;
}
