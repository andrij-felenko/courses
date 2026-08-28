#include <AccelStepper.h>

// HALF4WIRE = half-step, 4 керовані виводи. Далі — піни в порядку 1-3-2-4:
//   IN1=8, IN3=10, IN2=9, IN4=11  (дроти на платі — по-порядку!)
AccelStepper motor(AccelStepper::HALF4WIRE, 8, 10, 9, 11);

const long HALFSTEPS_PER_REV = 4076;   // півкроків на оберт (half-step!)

void setup() {
  motor.setMaxSpeed(700.0);        // стеля швидкості, кроків/с
  motor.setAcceleration(400.0);    // розгін/гальмування, кроків/с²
  motor.moveTo(HALFSTEPS_PER_REV); // ціль: один оберт уперед (абсолютна позиція)
}

void loop() {
  // run() робить максимум один крок за виклик і ЗАРАЗ ЖЕ повертає керування.
  // Мотор сам розганяється й гальмує до цілі. Клич це якнайчастіше.
  motor.run();

  // Доїхали до цілі? Задамо нову — поїде назад у нуль.
  if (motor.distanceToGo() == 0) {
    long here = motor.currentPosition();
    motor.moveTo(here == 0 ? HALFSTEPS_PER_REV : 0);
  }
}
