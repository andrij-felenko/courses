// esp32-fan-thermal.ino — швидкість за температурою + сторож обертів
#include <Arduino.h>
#include "driver/pulse_cnt.h"

const int PWM_PIN  = 25;
const int PWM_FREQ = 25000;   // 25 кГц — генерацію див. у рецепті ШІМ
const int PWM_BITS = 8;
const int TACH_PIN = 27;
const int DUTY_MAX = (1 << PWM_BITS) - 1;

pcnt_unit_handle_t    unit = nullptr;   // лічильник обертів
pcnt_channel_handle_t chan = nullptr;   // (налаштування — у рецепті TACH)

float readTempC();       // ← ваш давач (NTC, DS18B20, BME280 — байдуже)
void  tachPcntBegin();   // ← як у рецепті з апаратним лічильником PCNT

uint8_t tempToPercent(float t) {
  const float tMin = 35.0f, tMax = 65.0f;
  if (t <= tMin) return 0;
  if (t >= tMax) return 100;
  return (uint8_t)((t - tMin) / (tMax - tMin) * 100.0f);
}

void fanSetSpeed(uint8_t percent) {     // деталі — у рецепті ШІМ
  if (percent > 100) percent = 100;
  ledcWrite(PWM_PIN, (uint32_t)percent * DUTY_MAX / 100);
}

void setup() {
  Serial.begin(115200);
  ledcAttach(PWM_PIN, PWM_FREQ, PWM_BITS);
  pinMode(TACH_PIN, INPUT_PULLUP);
  tachPcntBegin();
}

uint8_t  deadSeconds = 0;    // скільки секунд поспіль наказ є, а обертів нема
uint32_t lastMs = 0;

void loop() {
  uint32_t now = millis();
  if (now - lastMs < 1000) return;      // один крок керування на секунду
  lastMs = now;

  float   t   = readTempC();
  uint8_t pct = tempToPercent(t);
  fanSetSpeed(pct);

  int count = 0;
  pcnt_unit_get_count(unit, &count);
  pcnt_unit_clear_count(unit);
  uint32_t rpm = (count / 2) * 60;      // ÷2 (2 імпульси/оберт) ×60 (у хвилини)

  // Сторож зі стартовою відстрочкою (нижче — чому не «в лоб»)
  if (pct > 0 && rpm == 0) {
    if (deadSeconds < 255) deadSeconds++;
  } else {
    deadSeconds = 0;                     // закрутився або наказ знято — лічильник у нуль
  }
  if (deadSeconds >= 3) {                // 3 с наказу без жодного оберту — біда
    Serial.println("!!! ТРИВОГА: наказано крутитися, а обертів нема — перевір вентилятор");
    // тут: аварійний вихід, скид навантаження, зниження тактової тощо
  }

  Serial.printf("t=%.1f°C  швидкість=%u%%  оберти=%u об/хв\n", t, pct, rpm);
}
