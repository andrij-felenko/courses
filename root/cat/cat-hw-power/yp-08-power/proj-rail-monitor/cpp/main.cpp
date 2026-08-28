// Arduino (ATmega328, напр. Uno/Nano) — рейка 5 В.
// Опора — ВНУТРІШНІ 1.1 В (не пливуть за живленням!),
// тож дільник масштабуємо саме під 1.1 В, а не під 5 В.
// Щоб 5.2 В рейки давали <1.1 В у вузлі: k ≈ 0.2 → R1=39к, R2=10к.
//   Uвузол(5.2) = 5.2 · 10/49 = 1.06 В  ✓ під 1.1 В
//   Uрейки = Uвузол · (39+10)/10 = Uвузол · 4.9

const uint8_t  PIN_RAIL = A0;
const float    R1 = 39000.0f,  R2 = 10000.0f;
const float    VREF = 1.100f;              // внутрішнє джерело ATmega328
const float    DIV  = (R1 + R2) / R2;      // = 4.9, обернений коефіцієнт
const float    BROWNOUT = 4.6f;            // поріг тривоги, В

void setup() {
  Serial.begin(115200);
  analogReference(INTERNAL);               // опора = 1.1 В, НЕ живлення
  analogRead(PIN_RAIL);                    // перше читання — «розігнати» опору
  delay(2);
}

float readRailVolts() {
  // усереднення 8 вибірок прибирає шум молодшого розряду
  uint32_t acc = 0;
  for (uint8_t i = 0; i < 8; i++) acc += analogRead(PIN_RAIL);
  float code = acc / 8.0f;                 // 0..1023 (10-біт)
  float vNode = code * VREF / 1023.0f;     // напруга на піні
  return vNode * DIV;                      // назад у напругу рейки
}

void loop() {
  float v = readRailVolts();
  if (v < BROWNOUT) {
    Serial.print("BROWNOUT! рейка = ");
    Serial.print(v, 2);
    Serial.println(" В");
    // тут-таки реакція: запалити червоний LED, скинути навантаження…
  } else {
    Serial.print("рейка OK: ");
    Serial.print(v, 2);
    Serial.println(" В");
  }
  delay(200);
}
