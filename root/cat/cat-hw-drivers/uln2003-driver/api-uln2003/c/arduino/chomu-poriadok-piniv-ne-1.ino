#include <Stepper.h>

// Кроків на оберт для Stepper — тут число ПОВНИХ кроків вала.
const int STEPS_PER_REV = 2038;   // ≈ 32 · 63.684 (НЕ 2048!)

// УВАГА на порядок аргументів. Дроти: D8→IN1, D9→IN2, D10→IN3, D11→IN4.
// Але в конструктор піни йдуть у магнітному порядку обмоток 1-3-2-4:
//   IN1=8,  IN3=10,  IN2=9,  IN4=11
Stepper motor(STEPS_PER_REV, 8, 10, 9, 11);

void setup() {
  motor.setSpeed(10);   // швидкість в обертах за хвилину (об/хв)
}

void loop() {
  motor.step(STEPS_PER_REV);    // рівно один оберт вперед
  delay(1000);
  motor.step(-STEPS_PER_REV);   // один оберт назад (знак = напрям)
  delay(1000);
}
