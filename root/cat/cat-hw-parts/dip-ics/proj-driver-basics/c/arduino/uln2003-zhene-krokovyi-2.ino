// Той самий мотор через стандартну бібліотеку Stepper.
// КЛЮЧОВЕ: порядок ніг у конструкторі — 1-3-2-4, а не 1-2-3-4,
// бо саме так фізично намотані фази 28BYJ-48. Інакше — тремтіння на місці.
#include <Stepper.h>

const int STEPS_PER_REV = 2048;   // повних кроків на оберт валу (після редуктора)
// ноги: IN1, IN3, IN2, IN4  ← переставлено 3 і 2 місцями!
Stepper motor(STEPS_PER_REV, 8, 10, 9, 11);

void setup() {
  motor.setSpeed(10);             // об/хв
}

void loop() {
  motor.step(STEPS_PER_REV);      // один оберт уперед
  delay(500);
  motor.step(-STEPS_PER_REV);     // один оберт назад
  delay(500);
}
