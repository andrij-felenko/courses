#include <Arduino.h>

const int SENSOR_PIN = A0;             // Аналоговий вхід давача ACS712
const int RELAY_PIN = 7;               // Цифровий вихід керування реле
const float SENSITIVITY = 0.185;       // 185 мВ/А для модифікації 5A (0.185 В/А)
const float VCC_VOLTAGE = 5.0;         // Опорна напруга живлення (5.0 В)
const float MAINS_VOLTAGE = 230.0;     // Напруга електромережі в Вольтах
const float OVERCURRENT_LIMIT = 4.5;   // Граничний поріг струму для відсікання (А)
const int CALIB_SAMPLES = 100;         // Кількість вибірок у спокої
const int RMS_SAMPLES = 200;           // Кількість вибірок за 1 період (20 мс)

float vZeroCalib = 2.5;                // Початкове теоретичне значення VCC / 2

float calibrateZeroOffset() {
  long rawSum = 0;
  Serial.println(F("Калібрування нуля... Переконайтеся, що струм відсутній."));
  
  for (int i = 0; i < CALIB_SAMPLES; i++) {
    rawSum += analogRead(SENSOR_PIN);
    delay(2);
  }
  
  float avgRaw = static_cast<float>(rawSum) / CALIB_SAMPLES;
  float zeroVolt = (avgRaw / 1023.0) * VCC_VOLTAGE;
  Serial.print(F("Калібрування завершено. Напруга спокою V_zero = "));
  Serial.print(zeroVolt, 3);
  Serial.println(F(" В"));
  return zeroVolt;
}

float calculateRMSCurrent() {
  float sumSq = 0.0;
  
  for (int i = 0; i < RMS_SAMPLES; i++) {
    int rawVal = analogRead(SENSOR_PIN);
    float vOut = (rawVal / 1023.0) * VCC_VOLTAGE;
    float iInst = (vOut - vZeroCalib) / SENSITIVITY;
    
    sumSq += iInst * iInst;
    delayMicroseconds(100);
  }
  
  float meanSq = sumSq / RMS_SAMPLES;
  return sqrt(meanSq);
}

void setup() {
  Serial.begin(115200);
  pinMode(RELAY_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, HIGH); // Початково реле ввімкнено
  
  delay(500);
  vZeroCalib = calibrateZeroOffset();
  Serial.println(F("Запуск моніторингу потужності..."));
}

void loop() {
  float currentRMS = calculateRMSCurrent();
  float powerWatt = currentRMS * MAINS_VOLTAGE;
  
  Serial.print(F("Струм RMS: "));
  Serial.print(currentRMS, 3);
  Serial.print(F(" A | Потужність: "));
  Serial.print(powerWatt, 1);
  Serial.println(F(" Вт"));
  
  if (currentRMS > OVERCURRENT_LIMIT) {
    digitalWrite(RELAY_PIN, LOW); // Розмикаємо коло
    Serial.print(F("УВАГА: Перевищення граничного струму "));
    Serial.print(currentRMS, 2);
    Serial.println(F(" А! Реле вимкнено!"));
    
    while (true) {
      delay(1000);
    }
  }
  
  delay(1000);
}
