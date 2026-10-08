#include <Arduino.h>

const int PUMP_PWM_PIN = 9;
const int CURRENT_SENSE_PIN = A0;
const int PRESSURE_SENSE_PIN = A1;
const int CURRENT_LIMIT = 800; // Порогове значення АЦП для струму

void setup() {
    pinMode(PUMP_PWM_PIN, OUTPUT);
    analogWrite(PUMP_PWM_PIN, 0);
    Serial.begin(115200);
}

void setPumpSpeed(uint8_t speedPercent) {
    // Зчитування зворотного зв'язку за струмом
    int currentRaw = analogRead(CURRENT_SENSE_PIN);
    
    if (currentRaw > CURRENT_LIMIT) {
        // Аварійне зупинення приводу під час перевантаження
        analogWrite(PUMP_PWM_PIN, 0);
        Serial.println("УВАГА: Перевантаження помпи за струмом!");
        return;
    }

    // Масштабування відсотків 0-100% у ШІМ 0-255
    uint8_t pwmValue = map(speedPercent, 0, 100, 0, 255);
    analogWrite(PUMP_PWM_PIN, pwmValue);
}

void loop() {
    // Приклад керування продуктивністю з опитуванням тиску
    int pressureRaw = analogRead(PRESSURE_SENSE_PIN);
    
    // Плавний пуск та підтримання режиму
    setPumpSpeed(75);
    delay(100);
}
