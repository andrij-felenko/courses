#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

Adafruit_PWMServoDriver pca = Adafruit_PWMServoDriver(0x40);  // адреса за замовчуванням

const float STEP_US = 20000.0 / 4096.0;   // ≈ 4.88 мкс на крок при 50 Гц

// ширина імпульсу (мкс) -> момент вимкнення лічильника (0..4095)
uint16_t usToTicks(int us) {
  return (uint16_t)(us / STEP_US + 0.5);   // округлення до найближчого кроку
}

void servoUs(uint8_t ch, int us) {
  us = constrain(us, 1000, 2000);          // тримаємось безпечних меж SG90
  pca.setPWM(ch, 0, usToTicks(us));        // імпульс: увімк на кроці 0, вимк на usToTicks
}

void setup() {
  Wire.begin();
  pca.begin();
  pca.setPWMFreq(50);        // 50 Гц на ВСІ 16 каналів одразу
  // приклад: розвести три серва по нейтралі
  servoUs(0, 1500);
  servoUs(1, 1500);
  servoUs(2, 1500);
}

void loop() {
  // махнути каналом 0 туди-сюди, решта стоять
  servoUs(0, 1000); delay(800);
  servoUs(0, 2000); delay(800);
}
