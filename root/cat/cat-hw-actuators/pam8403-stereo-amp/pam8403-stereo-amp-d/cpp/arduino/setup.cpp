// Приклад безшумного увімкнення підсилювача PAM8403 на Arduino
const int PIN_SHDN = 4;
const int PIN_MUTE = 5;

void setup() {
  // Налаштовуємо виводи керування як виходи
  pinMode(PIN_SHDN, OUTPUT);
  pinMode(PIN_MUTE, OUTPUT);

  // Початковий стан: підсилювач вимкнено, звук приглушено
  digitalWrite(PIN_SHDN, LOW);
  digitalWrite(PIN_MUTE, LOW);

  // Очікуємо стабілізації живлення VCC
  delay(100);

  // Крок 1: Вмикаємо внутрішню аналогову схему
  digitalWrite(PIN_SHDN, HIGH);

  // Крок 2: Пауза для завершення заряду вхідних конденсаторів
  delay(50);

  // Крок 3: Активуємо передачу аудіосигналу
  digitalWrite(PIN_MUTE, HIGH);
}

void loop() {
  // Основний цикл роботи пристрою
}
