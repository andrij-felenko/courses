#include <Arduino.h>

const uint8_t HALL_SENSOR_PIN = 2;
volatile uint32_t pulseCount = 0;

void IRAM_ATTR onHallSensorChange() {
  pulseCount++;
}

void setup() {
  Serial.begin(115200);
  pinMode(HALL_SENSOR_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(HALL_SENSOR_PIN), onHallSensorChange, CHANGE);
}

void loop() {
  static uint32_t lastPrintTime = 0;
  if (millis() - lastPrintTime >= 1000) {
    lastPrintTime = millis();
    Serial.print("Кількість перемикань полюсів: ");
    Serial.println(pulseCount);
  }
}
