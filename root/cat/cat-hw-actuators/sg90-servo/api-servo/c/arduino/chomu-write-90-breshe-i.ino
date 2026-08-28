#include <Servo.h>
Servo sg90;

void setup() {
  sg90.attach(9);
}

void loop() {
  sg90.writeMicroseconds(1000);   // одне крайнє — задаємо ширину НАПРЯМУ
  delay(1000);
  sg90.writeMicroseconds(1500);   // справжня нейтраль (для цього екземпляра)
  delay(1000);
  sg90.writeMicroseconds(2000);   // інше крайнє
  delay(1000);
}
