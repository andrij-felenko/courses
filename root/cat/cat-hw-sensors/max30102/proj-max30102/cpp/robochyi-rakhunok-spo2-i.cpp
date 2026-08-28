#include <Wire.h>
#include "MAX30105.h"
#include "spo2_algorithm.h"

MAX30105 particleSensor;

// 18-бітні відліки: на «великих» МК — 32 біти, на ATmega328 — 16 (заради пам'яті)
#if defined(__AVR_ATmega328P__) || defined(__AVR_ATmega168__)
  uint16_t irBuffer[100];
  uint16_t redBuffer[100];
#else
  uint32_t irBuffer[100];
  uint32_t redBuffer[100];
#endif

int32_t bufferLength = 100;   // розмір вікна (≈1 с при 100 відл./с)
int32_t spo2;                 // порахований SpO2
int8_t  validSPO2;            // прапорець достовірності SpO2
int32_t heartRate;            // порахований пульс
int8_t  validHeartRate;       // прапорець достовірності пульсу

void setup() {
  Serial.begin(115200);
  if (!particleSensor.begin(Wire, I2C_SPEED_FAST)) {
    Serial.println(F("Чип не знайдено."));
    while (1);
  }
  // Явний набір під SpO2: два світлодіоди, 100 відл./с назовні (400/4)
  particleSensor.setup(0x1F, 4, 2, 400, 411, 4096);
  Serial.println(F("Прикладіть палець нерухомо."));
}

void loop() {
  // 1. НАБРАТИ перше вікно: 100 пар відліків
  for (byte i = 0; i < bufferLength; i++) {
    while (particleSensor.available() == false)   // чекаємо новий відлік…
      particleSensor.check();                      // …підкачуючи FIFO з чипа

    redBuffer[i] = particleSensor.getRed();
    irBuffer[i]  = particleSensor.getIR();
    particleSensor.nextSample();                    // крок до наступної пари
  }

  // 2. ПОРАХУВАТИ по повному вікну. Зверни увагу на &: віддаємо адреси,
  //    бо функція кладе результати назад у ці змінні.
  maxim_heart_rate_and_oxygen_saturation(
      irBuffer, bufferLength, redBuffer,
      &spo2, &validSPO2, &heartRate, &validHeartRate);

  // 3. Далі — ковзне вікно: викидаємо 25 найстаріших, добираємо 25 свіжих,
  //    перераховуємо. Оновлення ~4 рази/с без пауз між вимірами.
  while (1) {
    for (byte i = 25; i < 100; i++) {               // зсунути хвіст уперед
      redBuffer[i - 25] = redBuffer[i];
      irBuffer[i - 25]  = irBuffer[i];
    }
    for (byte i = 75; i < 100; i++) {               // добрати 25 нових у кінець
      while (particleSensor.available() == false)
        particleSensor.check();
      redBuffer[i] = particleSensor.getRed();
      irBuffer[i]  = particleSensor.getIR();
      particleSensor.nextSample();
    }

    maxim_heart_rate_and_oxygen_saturation(
        irBuffer, bufferLength, redBuffer,
        &spo2, &validSPO2, &heartRate, &validHeartRate);

    // Показуємо лише те, чому алгоритм довіряє
    Serial.print(F("HR="));
    if (validHeartRate) Serial.print(heartRate); else Serial.print(F("--"));
    Serial.print(F(" bpm, SpO2="));
    if (validSPO2) { Serial.print(spo2); Serial.print(F(" %")); }
    else            Serial.print(F("-- %"));
    Serial.println();
  }
}
