#include <Arduino.h>

const int ADC_PIN = A0;
const float VREF = 5.0;            // Опорна напруга (В)
const float ADC_MAX = 1024.0;      // 10-бітний АЦП
const float SENSITIVITY = 0.185;   // Чутливість 185 мВ/А для ACS712-05B

float zeroVoltage = 2.5;

void calibrateZero() {
  long sum = 0;
  for (int i = 0; i < 500; i++) {
    sum += analogRead(ADC_PIN);
    delay(1);
  }
  float avgRaw = (float)sum / 500.0;
  zeroVoltage = (avgRaw * VREF) / ADC_MAX;
}

float calculateRMS() {
  float sumSquares = 0.0;
  int samples = 0;
  unsigned long startTime = millis();

  // Збір вибірок протягом 40 мс (2 періоди мережі 50 Гц)
  while (millis() - startTime < 40) {
    int raw = analogRead(ADC_PIN);
    float voltage = ((float)raw * VREF) / ADC_MAX;
    float current = (voltage - zeroVoltage) / SENSITIVITY;
    sumSquares += current * current;
    samples++;
  }

  if (samples == 0) return 0.0;
  return sqrt(sumSquares / samples);
}
