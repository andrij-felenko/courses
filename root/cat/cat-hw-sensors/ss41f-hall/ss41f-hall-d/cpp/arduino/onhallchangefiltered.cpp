#include <Arduino.h>

const uint8_t HALL_PIN = 2;
const uint32_t MIN_PULSE_INTERVAL_US = 500; // 500 мікросекунд фільтрації

volatile uint32_t validPulseCount = 0;
volatile uint32_t lastInterruptTimeUs = 0;

void IRAM_ATTR onHallChangeFiltered() {
  uint32_t currentTimeUs = micros();
  if (currentTimeUs - lastInterruptTimeUs >= MIN_PULSE_INTERVAL_US) {
    validPulseCount++;
    lastInterruptTimeUs = currentTimeUs;
  }
}

void setup() {
  Serial.begin(115200);
  pinMode(HALL_PIN, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(HALL_PIN), onHallChangeFiltered, CHANGE);
}

void loop() {
  static uint32_t lastPrintMs = 0;
  if (millis() - lastPrintMs >= 1000) {
    lastPrintMs = millis();
    Serial.print("Відфільтрована кількість імпульсів: ");
    Serial.println(validPulseCount);
  }
}
