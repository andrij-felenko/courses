#include <Arduino.h>

const uint8_t BOOST_EN_PIN = 4;
const uint8_t BATT_ADC_PIN = A0;

// Пороги напруги у мілівольтах
const uint32_t UVLO_SHUTDOWN_MV = 2700;
const uint32_t UVLO_RECOVERY_MV = 3000;

bool isPowerEnabled = true;

void setup() {
    pinMode(BOOST_EN_PIN, OUTPUT);
    digitalWrite(BOOST_EN_PIN, HIGH); // Тримати підвищувач увімкненим
}

void loop() {
    // Зчитування напруги джерела живлення через коефіцієнт дільника
    uint32_t rawAdc = analogRead(BATT_ADC_PIN);
    uint32_t batteryMv = (rawAdc * 3300UL * 2UL) / 1023UL; // Приклад дільника 1:1

    if (isPowerEnabled && (batteryMv < UVLO_SHUTDOWN_MV)) {
        digitalWrite(BOOST_EN_PIN, LOW); // Аварійне вимкнення
        isPowerEnabled = false;
    } else if (!isPowerEnabled && (batteryMv > UVLO_RECOVERY_MV)) {
        digitalWrite(BOOST_EN_PIN, HIGH); // Відновлення роботи після зарядки
        isPowerEnabled = true;
    }
    delay(500);
}
