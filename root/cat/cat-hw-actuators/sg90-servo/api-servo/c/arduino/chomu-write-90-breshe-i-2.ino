#include <Servo.h>
Servo sg90;

// Калібрувальні межі КОНКРЕТНОГО серва — знайдені дослідом (див. нижче).
// Стартові безпечні значення; уточніть під свій екземпляр.
const int US_MIN = 1000;   // ширина для 0°
const int US_MAX = 2000;   // ширина для 180°

void setup() {
  Serial.begin(115200);
  sg90.attach(9);
}

// Наш власний перерахунок кут → мікросекунди за ВІДКАЛІБРОВАНИМИ межами.
int angleToUs(int deg) {
  deg = constrain(deg, 0, 180);
  return map(deg, 0, 180, US_MIN, US_MAX);   // лінійно між нашими межами
}

void writeAngle(int deg) {
  sg90.writeMicroseconds(angleToUs(deg));
}

void loop() {
  // Приймаємо кут із монітора порту: надрукуйте число 0..180 і Enter.
  if (Serial.available()) {
    int deg = Serial.parseInt();
    if (deg >= 0 && deg <= 180) {
      writeAngle(deg);
      Serial.print("кут ");
      Serial.print(deg);
      Serial.print("° -> ");
      Serial.print(angleToUs(deg));
      Serial.println(" мкс");
    }
  }
}
