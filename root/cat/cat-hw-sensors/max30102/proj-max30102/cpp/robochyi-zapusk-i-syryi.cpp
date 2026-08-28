#include <Wire.h>
#include "MAX30105.h"

MAX30105 particleSensor;

void setup() {
  Serial.begin(115200);
  Serial.println(F("MAX30102 — запуск"));

  // begin() ШУКАЄ чип. I2C_SPEED_FAST = 400 кГц (швидкий режим шини).
  // На ESP32/RP2040/STM32 спершу задайте свої ніжки: Wire.begin(SDA, SCL).
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println(F("Чип не знайдено. Перевір живлення, дроти SDA/SCL, підтяжки."));
    while (1);              // далі рухатись немає сенсу
  }
  Serial.println(F("Чип знайдено. Прикладіть палець рівно, без натиску."));

  // setup() НАЛАШТОВУЄ. Беремо явно свій набір, а не мовчазні замовчування.
  byte powerLevel   = 0x1F;   // ~6.4 мА, спокійний старт
  byte sampleAvg    = 4;      // усереднити по 4 — тихіший сигнал
  byte ledMode      = 2;      // 2 = червоний + інфрачервоний (треба для SpO2)
  byte sampleRate   = 400;    // 400 фіз. відліків/с
  int  pulseWidth   = 411;    // довгий спалах — краще розрізнення
  int  adcRange     = 4096;   // межа шкали АЦП
  particleSensor.setup(powerLevel, sampleAvg, ledMode, sampleRate, pulseWidth, adcRange);
}

void loop() {
  long ir  = particleSensor.getIR();    // миттєве інфрачервоне число
  long red = particleSensor.getRed();   // миттєве червоне число

  Serial.print(F("IR="));  Serial.print(ir);
  Serial.print(F(" RED=")); Serial.print(red);

  if (ir < 50000) Serial.print(F("   — пальця немає?"));  // поріг присутності
  Serial.println();
}
