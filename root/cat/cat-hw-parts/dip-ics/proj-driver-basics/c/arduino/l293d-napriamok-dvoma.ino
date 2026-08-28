// L293D, перший міст: мотор між OUT1 (вивід 3) і OUT2 (вивід 6).
// EN1 (вивід 1) — на ногу з ШІМ (позначені ~ на платі).
// IN1 (вивід 2) і IN2 (вивід 7) — на будь-які цифрові ноги.
// Vss (вивід 16) = 5V логіки; Vs (вивід 8) = живлення мотора; GND (4,5,12,13) спільна з МК.
const int EN1 = 9;    // мусить бути ШІМ-нога (~9 на Uno/Nano)
const int IN1 = 4;
const int IN2 = 5;

void forward(uint8_t speed) {   // speed 0..255 — глибина ШІМ
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  analogWrite(EN1, speed);      // ШІМ на enable = оберти
}

void backward(uint8_t speed) {
  digitalWrite(IN1, LOW);
  digitalWrite(IN2, HIGH);
  analogWrite(EN1, speed);
}

void brake() {                  // динамічне гальмо: enable є, входи однакові
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, HIGH);
  analogWrite(EN1, 255);        // міст увімкнено на повну, обмотка закорочена
}

void coast() {                  // вільний хід: enable знято
  analogWrite(EN1, 0);          // байдуже, що на входах
}

void setup() {
  pinMode(EN1, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
}

void loop() {
  forward(180);   delay(1500);  // вперед на ~70% обертів
  coast();        delay(500);   // відпустили — котиться
  backward(120);  delay(1500);  // назад повільніше
  brake();        delay(500);   // різко спинили
}
