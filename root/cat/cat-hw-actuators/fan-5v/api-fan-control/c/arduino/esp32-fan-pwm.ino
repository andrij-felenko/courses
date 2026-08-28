// esp32-fan-pwm.ino — 25-кГц ШІМ на вивід PWM вентилятора (Arduino-ESP32 3.x)
#include <Arduino.h>

const int   PWM_PIN  = 25;       // будь-який GPIO, здатний на вихід LEDC
const int   PWM_FREQ = 25000;    // 25 кГц — вище за поріг слуху (спец. Intel: 21–28 кГц)
const int   PWM_BITS = 8;        // 8-бітна розрядність → duty 0…255
const int   DUTY_MAX = (1 << PWM_BITS) - 1;   // 255

void fanSetSpeed(uint8_t percent) {           // 0…100 % → duty
  if (percent > 100) percent = 100;
  uint32_t duty = (uint32_t)percent * DUTY_MAX / 100;
  ledcWrite(PWM_PIN, duty);                    // у 3.x аргумент — сам вивід, не канал
}

void setup() {
  // один виклик: налаштувати частоту+розрядність і прив'язати вивід
  ledcAttach(PWM_PIN, PWM_FREQ, PWM_BITS);
  fanSetSpeed(50);                             // старт на 50 %
}

void loop() {
  // повільний «вдих-видих» швидкістю, щоб почути (точніше — НЕ почути) роботу
  for (int p = 20; p <= 100; p += 5) { fanSetSpeed(p); delay(200); }
  for (int p = 100; p >= 20; p -= 5) { fanSetSpeed(p); delay(200); }
}
