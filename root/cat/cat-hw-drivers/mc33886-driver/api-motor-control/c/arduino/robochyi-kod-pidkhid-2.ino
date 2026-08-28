// ── MC33886: ШІМ прямо на IN, EN тримаємо ввімкненим. Arduino ──
// Швидкість модулюється на одній ніжці напрямку; друга — стала.
// У паузах ШІМ мотор у стані 0 0 (гальмо) → жорсткіший «повільний спад».

const uint8_t PIN_IN1 = 9;    // ОБИДВІ ніжки напрямку — ШІМ-здатні («~»)!
const uint8_t PIN_IN2 = 10;   // бо ШІМ подаємо то на одну, то на іншу
const uint8_t PIN_EN  = 4;    // просто «ввімкнено», звичайна цифрова

void setup() {
  pinMode(PIN_IN1, OUTPUT);
  pinMode(PIN_IN2, OUTPUT);
  pinMode(PIN_EN,  OUTPUT);
  digitalWrite(PIN_EN, HIGH);       // міст живий увесь час
  motorCoast();
}

// Уперед: IN1=0 сталий, ШІМ на IN2. duty 0..255.
void motorForward(uint8_t duty) {
  digitalWrite(PIN_IN1, LOW);
  analogWrite(PIN_IN2, duty);       // імпульс: 0 1 (хід); пауза: 0 0 (гальмо)
}

// Назад: IN2=0 сталий, ШІМ на IN1.
void motorReverse(uint8_t duty) {
  digitalWrite(PIN_IN2, LOW);
  analogWrite(PIN_IN1, duty);       // імпульс: 1 0 (хід); пауза: 0 0 (гальмо)
}

void motorBrake() {
  analogWrite(PIN_IN1, 0);          // тут analogWrite(…,0) == LOW
  analogWrite(PIN_IN2, 0);          // 0 0 постійно → тримаюче гальмо
}

void motorCoast() {
  digitalWrite(PIN_EN, LOW);        // єдиний спосіб вибігу тут — зняти EN
  digitalWrite(PIN_IN1, LOW);
  digitalWrite(PIN_IN2, LOW);
}

void loop() {
  digitalWrite(PIN_EN, HIGH);
  motorForward(180);   delay(1500);
  motorReverse(120);   delay(1500);
  motorBrake();        delay(800);
}
