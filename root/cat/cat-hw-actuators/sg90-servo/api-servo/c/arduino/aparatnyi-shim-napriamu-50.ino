// ESP32, Arduino-core 3.x. Прямий апаратний ШІМ через LEDC, без бібліотеки Servo.
const int  SERVO_PIN  = 18;
const int  SERVO_FREQ = 50;        // 50 Гц = період 20 мс
const int  SERVO_BITS = 16;        // роздільність лічильника
const long PERIOD_US  = 20000;     // 1/50 Гц у мікросекундах

// перерахунок ширини імпульсу (мкс) у код заповнення LEDC
uint32_t usToDuty(int us) {
  long maxCount = (1L << SERVO_BITS) - 1;     // 65535 для 16 біт
  return (uint32_t)((long)us * maxCount / PERIOD_US);
}

void servoWriteUs(int us) {
  us = constrain(us, 1000, 2000);             // не гнати за реальні межі!
  ledcWrite(SERVO_PIN, usToDuty(us));
}

void setup() {
  ledcAttach(SERVO_PIN, SERVO_FREQ, SERVO_BITS);   // частота + роздільність + ніжка
  servoWriteUs(1500);                              // нейтраль
}

void loop() {
  servoWriteUs(1000); delay(1000);   // 0°
  servoWriteUs(1500); delay(1000);   // 90°
  servoWriteUs(2000); delay(1000);   // 180°
}
