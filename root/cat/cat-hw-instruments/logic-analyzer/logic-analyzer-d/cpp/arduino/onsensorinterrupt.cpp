#include <Arduino.h>

constexpr uint8_t DIAG_PIN = 4;
constexpr uint8_t SENSOR_INT_PIN = 2;

// Обробник переривання з прямим доступом до регістрів порту
void IRAM_ATTR onSensorInterrupt() {
    // Швидке встановлення високого рівня (Direct Register Access)
    GPIO.out_w1ts = (1u << DIAG_PIN);

    // Обробка апаратного сигналу периферії
    handleHardwareEvent();

    // Скидання діагностичного виводу в низький стан
    GPIO.out_w1tc = (1u << DIAG_PIN);
}
