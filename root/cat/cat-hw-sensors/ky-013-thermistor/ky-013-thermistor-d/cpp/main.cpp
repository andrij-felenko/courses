const uint8_t PIN_NTC = A0;      // сигнал S давача
const float   R_FIXED = 10000.0f; // сталий резистор на модулі, Ом
const float   R25     = 10000.0f; // опір термістора за 25 °C
const float   BETA    = 3950.0f;  // B-параметр термістора, K
const float   T25     = 298.15f;  // 25 °C у кельвінах

void setup() {
  Serial.begin(9600);            // пін аналоговий — pinMode не потрібен
}

float readTempC() {
  int   raw = analogRead(PIN_NTC);          // 0..1023
  float ratio = raw / 1023.0f;              // частка шкали = U_S / Vcc

  // Термістор у ВЕРХНЬОМУ плечі (між + і S), сталий резистор — знизу:
  //   U_S/Vcc = R_fixed / (R_ntc + R_fixed)  →  R_ntc = R_fixed*(1/ratio − 1)
  float r_ntc = R_FIXED * (1.0f / ratio - 1.0f);

  // B-формула: з опору назад у температуру (Vcc скоротилося саме)
  float invT = 1.0f / T25 + logf(r_ntc / R25) / BETA;
  return 1.0f / invT - 273.15f;             // назад у °C
}

void loop() {
  Serial.print(readTempC(), 1);
  Serial.println(" C");
  delay(500);
}
