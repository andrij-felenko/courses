// N20 через DRV8833, канал A. Плата Arduino Uno/Nano (ATmega328).
// AIN1 і AIN2 — на піни з апаратним ШІМ (позначені ~ на платі): 5 і 6.
const uint8_t AIN1 = 5;   // ~
const uint8_t AIN2 = 6;   // ~
const uint8_t SLP  = 4;   // nSLEEP драйвера (дозвіл силової частини)

void setup() {
  pinMode(AIN1, OUTPUT);
  pinMode(AIN2, OUTPUT);
  pinMode(SLP,  OUTPUT);
  digitalWrite(SLP, HIGH);      // будимо драйвер
  coast();                      // старт у безпечному стані — мотор відпущено
}

// Керуємо швидкістю зі знаком: +100 вперед на повну, -100 назад на повну, 0 стоп-вибіг.
// Схема «фазна»: один вхід тримає рівень (напрям), на другий кладемо ШІМ (швидкість).
void drive(int speed) {
  speed = constrain(speed, -100, 100);
  uint8_t duty = (uint8_t)(abs((long)speed) * 255 / 100);   // 0..100 % → 0..255
  if (speed >= 0) {            // ВПЕРЕД: AIN2=0, ШІМ на AIN1
    digitalWrite(AIN2, LOW);
    analogWrite(AIN1, duty);
  } else {                     // НАЗАД: AIN1=0, ШІМ на AIN2
    digitalWrite(AIN1, LOW);
    analogWrite(AIN2, duty);
  }
}

void brake() {                 // 1 1 → обидва виводи замкнено, різке гальмо
  digitalWrite(AIN1, HIGH);
  digitalWrite(AIN2, HIGH);
}

void coast() {                 // 0 0 → обидва виводи «висять», вибіг за інерцією
  digitalWrite(AIN1, LOW);
  digitalWrite(AIN2, LOW);
}

void loop() {
  // Плавний розгін уперед 0 → 100 %, коротка їзда, гальмо, пауза.
  for (int s = 0; s <= 100; s++) { drive(s); delay(20); }
  delay(1000);
  brake();
  delay(500);
  // Те саме назад.
  for (int s = 0; s >= -100; s--) { drive(s); delay(20); }
  delay(1000);
  coast();                     // відпускаємо — хай докотиться сам
  delay(1500);
}
