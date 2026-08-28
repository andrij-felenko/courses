#include <Arduino.h>
#include <math.h>

// ── Піни й сталі ─────────────────────────────────────────────
const int   AO_PIN   = A0;      // AO модуля → аналоговий вхід
const float ADC_MAX  = 1023.0f; // Arduino: 10-бітний АЦП
const float RL_KOHM  = 5.0f;    // навантажувальний резистор на платі (перевір!)
const float CLEAN_AIR_FACTOR = 9.83f;

struct MqCurve { float x, y, slope; };
const MqCurve LPG_CURVE = { 2.3f, 0.21f, -0.47f };

float R0 = 0.0f;                 // визначимо калібруванням у setup()

// ── Ланки ланцюжка ───────────────────────────────────────────
float mqReadRs(int raw) {
  if (raw <= 0) return INFINITY;
  return RL_KOHM * (ADC_MAX - (float)raw) / (float)raw;
}

float mqCalibrateR0(int pin) {
  float rsSum = 0.0f;
  for (int i = 0; i < 50; i++) { rsSum += mqReadRs(analogRead(pin)); delay(500); }
  return (rsSum / 50.0f) / CLEAN_AIR_FACTOR;
}

float mqPpm(float rsR0, const MqCurve& c) {
  return powf(10.0f, c.x + (log10f(rsR0) - c.y) / c.slope);
}

// ── Сторож порога з гістерезисом ─────────────────────────────
struct Hysteresis {
  float on, off; bool state = false;
  bool update(float v) {
    if (!state && v >= on)  state = true;
    if ( state && v <= off) state = false;
    return state;
  }
};
Hysteresis lpgWatch = { 350.0f, 250.0f };  // ppm-еквівалент LPG

void setup() {
  Serial.begin(9600);
  Serial.println(F("MQ: розпал... (даємо нагрівачу вийти на температуру)"));
  delay(30000);                     // короткий розпал; НЕ калібруй холодним давачем
  Serial.println(F("MQ: калібрую R0 у чистому повітрі..."));
  R0 = mqCalibrateR0(AO_PIN);       // роби це у справді чистому повітрі
  Serial.print(F("R0 = ")); Serial.print(R0); Serial.println(F(" кОм"));
}

void loop() {
  int   raw  = analogRead(AO_PIN);
  float rs   = mqReadRs(raw);
  float rsR0 = rs / R0;
  float ppm  = mqPpm(rsR0, LPG_CURVE);
  bool  alarm = lpgWatch.update(ppm);

  Serial.print(F("raw=")); Serial.print(raw);
  Serial.print(F("  Rs/R0=")); Serial.print(rsR0, 2);
  Serial.print(F("  LPG~")); Serial.print(ppm, 0); Serial.print(F(" ppm"));
  Serial.println(alarm ? F("  [ТРИВОГА]") : F(""));
  delay(1000);
}
