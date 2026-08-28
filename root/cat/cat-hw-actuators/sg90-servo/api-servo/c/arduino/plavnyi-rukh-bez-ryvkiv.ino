#include <Servo.h>
Servo sg90;

int   curAngle = 90;          // де серво зараз (наша модель)
int   tgtAngle = 90;          // куди хочемо
unsigned long lastStep = 0;   // коли робили крок востаннє
const unsigned long STEP_MS = 15;   // темп: 15 мс на градус

void setServoTarget(int deg) {        // задати нову ціль (миттєво повертається)
  tgtAngle = constrain(deg, 0, 180);
}

void updateServo() {                  // кликати ЩОРАЗУ в loop — рухає на 1 крок за раз
  if (curAngle == tgtAngle) return;                 // уже на місці — нема що робити
  unsigned long now = millis();
  if (now - lastStep < STEP_MS) return;             // ще рано для кроку
  lastStep = now;
  curAngle += (tgtAngle > curAngle) ? 1 : -1;       // один градус у бік цілі
  sg90.write(curAngle);
}

void setup() {
  sg90.attach(9);
  sg90.write(curAngle);
}

void loop() {
  updateServo();            // рух серва — неблокувальний, крок за кроком

  // ...тут вільно робимо будь-що інше: читаємо кнопки, давачі, мигаємо LED...
  // приклад: за командою з порту задаємо нову ціль — рух почнеться сам собою
  if (Serial.available()) {
    int deg = Serial.parseInt();
    if (deg >= 0 && deg <= 180) setServoTarget(deg);
  }
}
