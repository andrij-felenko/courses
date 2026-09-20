// Безпечна ініціалізація GPIO0 для керування Active-LOW реле
const int RELAY_PIN = 0;

void setup() {
  // 1. Попередньо записуємо логічну 1 (реле вимкнене)
  digitalWrite(RELAY_PIN, HIGH);
  // 2. Лише тепер активуємо вивід як вихід
  pinMode(RELAY_PIN, OUTPUT);
}

void loop() {
  // Приклад увімкнення реле (Active-LOW: логічний 0 вмикає)
  digitalWrite(RELAY_PIN, LOW);
  delay(1000);

  // Вимкнення реле (логічна 1 вимикає)
  digitalWrite(RELAY_PIN, HIGH);
  delay(1000);
}
