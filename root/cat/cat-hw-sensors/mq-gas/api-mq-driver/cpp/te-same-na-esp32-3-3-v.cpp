#include <Arduino.h>
#include <math.h>

const int   AO_PIN   = 34;        // ADC1-пін ESP32 (напр. GPIO34) через дільник
const float ADC_MAX  = 4095.0f;   // ESP32: 12-бітний АЦП
const float RL_KOHM  = 5.0f;      // навантажувальний резистор НА ПЛАТІ МОДУЛЯ
const float CLEAN_AIR_FACTOR = 9.83f;

// Зовнішній дільник AO→GPIO: R_top зверху, R_bot на землю.
// Він передає на вхід частку R_bot/(R_top+R_bot). Щоб відновити повну
// напругу давача, відлік домножуємо на обернений коефіцієнт.
const float DIV_TOP = 10.0f, DIV_BOT = 20.0f;
const float DIV_COMP = (DIV_TOP + DIV_BOT) / DIV_BOT;   // = 1.5

struct MqCurve { float x, y, slope; };
const MqCurve LPG_CURVE = { 2.3f, 0.21f, -0.47f };
float R0 = 0.0f;

// Відлік → Rₛ, з поправкою на зовнішній дільник ПЕРЕД математикою опору.
float mqReadRs(int raw) {
  float rawFull = (float)raw * DIV_COMP;              // повернули «повний» масштаб
  if (rawFull >= ADC_MAX) rawFull = ADC_MAX - 1;      // захист від ділення на 0
  if (rawFull <= 0)       return INFINITY;
  return RL_KOHM * (ADC_MAX - rawFull) / rawFull;
}

float mqCalibrateR0(int pin) {
  float rsSum = 0.0f;
  for (int i = 0; i < 50; i++) { rsSum += mqReadRs(analogRead(pin)); delay(500); }
  return (rsSum / 50.0f) / CLEAN_AIR_FACTOR;
}

float mqPpm(float rsR0, const MqCurve& c) {
  return powf(10.0f, c.x + (log10f(rsR0) - c.y) / c.slope);
}

struct Hysteresis {
  float on, off; bool state = false;
  bool update(float v) {
    if (!state && v >= on)  state = true;
    if ( state && v <= off) state = false;
    return state;
  }
};
Hysteresis lpgWatch = { 350.0f, 250.0f };

void setup() {
  Serial.begin(115200);
  analogSetAttenuation(ADC_11db);   // розширити діапазон АЦП ~до 3.3 В
  Serial.println("MQ: розпал...");
  delay(30000);                     // короткий розпал (новому давачу — доба випалу окремо)
  Serial.println("MQ: калібрую R0 у чистому повітрі...");
  R0 = mqCalibrateR0(AO_PIN);
  Serial.printf("R0 = %.2f кОм\n", R0);
}

void loop() {
  int   raw  = analogRead(AO_PIN);
  float rsR0 = mqReadRs(raw) / R0;
  float ppm  = mqPpm(rsR0, LPG_CURVE);
  bool  alarm = lpgWatch.update(ppm);
  Serial.printf("raw=%4d  Rs/R0=%.2f  LPG~%.0f ppm%s\n",
                raw, rsR0, ppm, alarm ? "  [ТРИВОГА]" : "");
  delay(1000);
}
