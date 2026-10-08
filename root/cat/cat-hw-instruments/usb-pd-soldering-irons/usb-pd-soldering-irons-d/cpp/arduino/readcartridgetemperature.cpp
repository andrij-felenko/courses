// Приклад циклу ШІМ-керування та вимірювання температури у C++ (Arduino Framework)
#include <Arduino.h>

const int pinHeaterMosfet = 9;
const int pinThermocoupleAdc = A0;

float readCartridgeTemperature() {
    // 1. Вимикаємо силовий ключ нагрівача (перехід у стан вимірювання)
    digitalWrite(pinHeaterMosfet, LOW);
    
    // 2. Часова затримка для стабілізації напруги на ЕРС термопари
    delayMicroseconds(1500);
    
    // 3. Зчитування напруги термопари через АЦП
    int adcValue = analogRead(pinThermocoupleAdc);
    
    // Перетворення значення в градуси Цельсія (ураховуючи підсилення ОП)
    float temperatureC = adcValue * (330.0 / 1023.0);
    return temperatureC;
}

void updateHeaterPwm(float targetTemp) {
    float currentTemp = readCartridgeTemperature();
    
    // Простий релейно-пропорційний вибір стану для демонстрації циклу
    if (currentTemp < targetTemp) {
        digitalWrite(pinHeaterMosfet, HIGH);
    } else {
        digitalWrite(pinHeaterMosfet, LOW);
    }
}
