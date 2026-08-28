const uint8_t LAMP_PIN = 9;  // вивід із апаратним PWM

void setup() { pinMode(LAMP_PIN, OUTPUT); }

void loop() {
  for (int duty = 0; duty <= 255; duty++) {  // плавне розгоряння
    analogWrite(LAMP_PIN, duty);             // 0 = темно, 255 = повний
    delay(8);
  }
  for (int duty = 255; duty >= 0; duty--) {  // плавне згасання
    analogWrite(LAMP_PIN, duty);
    delay(8);
  }
}
