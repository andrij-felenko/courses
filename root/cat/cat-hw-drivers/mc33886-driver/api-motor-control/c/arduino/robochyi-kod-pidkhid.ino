// ── MC33886: керування мотором. Arduino (Uno/Nano, ATmega328P) ──
// EN сидить на ШІМ-ніжці (позначена «~»); IN1/IN2 — звичайні цифрові.
// Швидкість — analogWrite(EN, 0..255); напрямок — рівні на IN1/IN2.

const uint8_t PIN_IN1 = 4;    // напрямок, будь-яка цифрова
const uint8_t PIN_IN2 = 7;    // напрямок, будь-яка цифрова
const uint8_t PIN_EN  = 9;    // ШІМ! на Uno/Nano ~ = 3,5,6,9,10,11

void setup() {
  pinMode(PIN_IN1, OUTPUT);
  pinMode(PIN_IN2, OUTPUT);
  pinMode(PIN_EN,  OUTPUT);
  motorCoast();               // старт у безпечному стані: міст вимкнено
}

// speed: 0..255 — шпаруватість ШІМ на EN (частка ввімкненого часу).
void motorForward(uint8_t speed) {
  digitalWrite(PIN_IN1, LOW);
  digitalWrite(PIN_IN2, HIGH);   // OUT1=−, OUT2=+  → один бік
  analogWrite(PIN_EN, speed);
}

void motorReverse(uint8_t speed) {
  digitalWrite(PIN_IN1, HIGH);
  digitalWrite(PIN_IN2, LOW);    // OUT1=+, OUT2=−  → інший бік
  analogWrite(PIN_EN, speed);
}

// Активне гальмо: обидва виходи на землю, обмотка закорочена.
void motorBrake() {
  digitalWrite(PIN_IN1, LOW);
  digitalWrite(PIN_IN2, LOW);    // 0 0 → мотор гальмує сам об себе
  analogWrite(PIN_EN, 255);      // міст має бути ВВІМКНЕНИЙ, щоб коротити
}

// Вільний вибіг: міст у тристейті, вал ніхто не тримає.
void motorCoast() {
  analogWrite(PIN_EN, 0);        // EN=0 → усі ключі відчеплені
}

void loop() {
  motorForward(180);   delay(1500);   // ~70% ходу вперед
  motorCoast();        delay(800);    // відпустили, дообертається
  motorReverse(120);   delay(1500);   // повільніше назад
  motorBrake();        delay(800);    // різко спинили
}
