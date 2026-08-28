/* arduino_supervisor.ino */
const int PIN_WDI = 7;
const int PIN_PFO_INTERRUPT = 2;
const int PIN_PERIPH_POWER = 8;

volatile bool powerLost = false;
unsigned long lastKickTime = 0;
const unsigned long MIN_WINDOW_MS = 35;
const unsigned long MAX_WINDOW_MS = 80;

void onPowerFail() {
  powerLost = true;
  digitalWrite(PIN_PERIPH_POWER, LOW); // Миттєво знеструмити навантаження
}

void setup() {
  pinMode(PIN_WDI, OUTPUT);
  pinMode(PIN_PERIPH_POWER, OUTPUT);
  digitalWrite(PIN_PERIPH_POWER, HIGH);

  pinMode(PIN_PFO_INTERRUPT, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(PIN_PFO_INTERRUPT), onPowerFail, FALLING);
  lastKickTime = millis();
}

void loop() {
  if (powerLost) {
    // Зупиняємося і не чіпаємо сторож — чекаємо апаратного скидання
    while (1) {}
  }

  // Виконання корисного алгоритму
  executeMainTasks();

  unsigned long now = millis();
  unsigned long elapsed = now - lastKickTime;

  // Скидання строго всередині відкритого вікна
  if (elapsed >= 50 && elapsed <= MAX_WINDOW_MS) {
    digitalWrite(PIN_WDI, !digitalRead(PIN_WDI));
    lastKickTime = now;
  }
}

void executeMainTasks() {
  delay(10); // Симуляція корисної роботи
}
