#include <Servo.h>
Servo esc;

const int ESC_PIN = 9;
const int POT_PIN = A0;   // потенціометр: середній вивід сюди, краї на +5В і GND

void setup() {
  esc.attach(ESC_PIN, 1000, 2000);
  esc.writeMicroseconds(1000);   // озброєння
  delay(3000);
}

void loop() {
  int raw = analogRead(POT_PIN);              // 0..1023 з АЦП
  int us  = map(raw, 0, 1023, 1000, 2000);    // перевести в 1000..2000 мкс
  esc.writeMicroseconds(us);
  delay(20);                                   // оновлювати раз на період
}
