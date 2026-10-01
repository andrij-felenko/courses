#include "ACS712.h"

const uint8_t SENSOR_PIN = A0;
const uint8_t RELAY_PIN = 8;
const float OVERCURRENT_LIMIT_A = 4.0f;
const float HYSTERESIS_A = 0.5f;

ACS712Sensor sensor(SENSOR_PIN, ACS712Model::ACS712_05B, 5.0f, 1024);

void setup() {
    Serial.begin(9600);
    pinMode(RELAY_PIN, OUTPUT);
    digitalWrite(RELAY_PIN, LOW);

    sensor.begin();

    Serial.println(F("Калібрування нуля ACS712 без струму..."));
    sensor.calibrateZero(100);
    Serial.println(F("Калібрування завершено."));
}

void loop() {
    float rmsCurrent = sensor.readCurrentRMS(50.0f);
    float powerWatts = rmsCurrent * 230.0f; // Приблизна потужність для 230 В

    bool isOverloaded = sensor.checkOvercurrent(OVERCURRENT_LIMIT_A, HYSTERESIS_A, RELAY_PIN);

    Serial.print(F("Струм RMS: "));
    Serial.print(rmsCurrent, 2);
    Serial.print(F(" A | Потужність: "));
    Serial.print(powerWatts, 1);
    Serial.print(F(" W | Захист: "));
    Serial.println(isOverloaded ? F("СПРАЦЮВАВ (ВІДКЛЮЧЕНО)") : F("НОРМА"));

    delay(500);
}
