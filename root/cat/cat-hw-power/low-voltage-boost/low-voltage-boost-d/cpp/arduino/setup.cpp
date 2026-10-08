#include <Arduino.h>

const int BATT_ADC_PIN = A0;
const int LOAD_ENABLE_PIN = 8;
const int MIN_BATT_VOLTAGE_MV = 950; // Поріг 0.95 В для запобігання просіданню

void setup() {
    Serial.begin(115200);
    pinMode(LOAD_ENABLE_PIN, OUTPUT);
    digitalWrite(LOAD_ENABLE_PIN, LOW); // Безпечний стан при старті

    // Зчитування вхідної напруги до вмикання силовиків
    int rawVal = analogRead(BATT_ADC_PIN);
    int battVoltageMw = map(rawVal, 0, 1023, 0, 5000); // Припускаємо подільник до 5 В

    Serial.print("Виміряна напруга живлення: ");
    Serial.print(battVoltageMw);
    Serial.println(" мВ");

    if (battVoltageMw >= MIN_BATT_VOLTAGE_MV) {
        Serial.println("Запуск периферичних модулів дозволено.");
        digitalWrite(LOAD_ENABLE_PIN, HIGH);
    } else {
        Serial.println("УВАГА: Низький заряд батареї! Систему переведено в економний режим.");
    }
}

void loop() {
    // Основний цикл роботи
}
