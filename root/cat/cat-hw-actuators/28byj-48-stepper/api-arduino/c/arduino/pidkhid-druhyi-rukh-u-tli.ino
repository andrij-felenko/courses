#include <AccelStepper.h>

// HALF4WIRE = напівкроковий, 4 керовані лінії — саме для 28BYJ-48 + ULN2003.
// І знову той самий порядок пінів: IN1, IN3, IN2, IN4  →  8, 10, 9, 11.
AccelStepper motor(AccelStepper::HALF4WIRE, 8, 10, 9, 11);

// У напівкроковому режимі кроків удвічі більше: ~4076 на оберт вала.
const long STEPS_PER_REV = 4076;

void setup() {
  motor.setMaxSpeed(1000.0);       // стеля швидкості, кроків за секунду
  motor.setAcceleration(500.0);    // прискорення, кроків за секунду за секунду
  motor.moveTo(STEPS_PER_REV);     // ціль: один повний оберт уперед
}

void loop() {
  // Доїхали до цілі? Розвернімося в протилежний бік.
  if (motor.distanceToGo() == 0) {
    motor.moveTo(-motor.currentPosition());
  }
  motor.run();                     // НЕблокуючий: щонайбільше один крок за виклик
}
