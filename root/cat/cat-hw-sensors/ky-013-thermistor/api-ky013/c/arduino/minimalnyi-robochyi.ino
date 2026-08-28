#include <math.h>

const uint8_t  PIN_NTC  = A0;        // сигнал S давача
const uint16_t ADC_MAX  = 1023;      // 10-біт АЦП: повна шкала (2^10 − 1)
const float    R_FIXED  = 10000.0f;  // сталий резистор на модулі, Ом
const float    R25      = 10000.0f;  // опір термістора за 25 °C, Ом
const float    BETA     = 3950.0f;   // B-параметр термістора, K
const float    T25_K    = 298.15f;   // 25 °C у кельвінах (25 + 273.15)

void setup() {
  Serial.begin(9600);                // пін аналоговий → pinMode НЕ потрібен
}

// відлік АЦП → опір термістора (термістор у ВЕРХНЬОМУ плечі)
float rawToResistance(uint16_t raw) {
  float ratio = (float)raw / ADC_MAX;             // U_S / Vcc, у межах 0..1
  // U_S/Vcc = R_fixed / (R_ntc + R_fixed)
  //        →  R_ntc = R_fixed * (1/ratio − 1)
  return R_FIXED * (1.0f / ratio - 1.0f);
}

// опір термістора → температура, °C (B-параметр)
float resistanceToTempC(float r_ntc) {
  // 1/T = 1/T25 + (1/B)·ln(R/R25)
  float invT = 1.0f / T25_K + logf(r_ntc / R25) / BETA;
  return 1.0f / invT - 273.15f;                   // K → °C
}

void loop() {
  uint16_t raw   = analogRead(PIN_NTC);
  float    r     = rawToResistance(raw);
  float    tempC = resistanceToTempC(r);

  Serial.print(tempC, 1);
  Serial.println(" C");
  delay(500);
}
