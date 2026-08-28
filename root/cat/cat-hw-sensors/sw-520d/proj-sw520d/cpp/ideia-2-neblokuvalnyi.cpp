const uint8_t PIN_SW    = 2;
const uint8_t PIN_LED   = 13;
const uint8_t ACTIVE    = LOW;
const uint16_t DEBOUNCE = 40;      // «глухе» вікно, мс — довше за брязкіт кульки

bool     lastStable = false;       // останній ПІДТВЕРДЖЕНИЙ стан (true = замкнено)
uint32_t lastEdgeMs = 0;           // коли востаннє прийняли зміну

void setup() {
  pinMode(PIN_SW, INPUT_PULLUP);
  pinMode(PIN_LED, OUTPUT);
  Serial.begin(115200);
}

// Повертає true рівно раз — у мить, коли давач ПІДТВЕРДЖЕНО замкнувся.
bool shockDetected() {
  bool raw = (digitalRead(PIN_SW) == ACTIVE);   // сирий рівень, ще з брязкотом

  // якщо стан не змінився — нічого не робимо
  if (raw == lastStable) return false;

  // стан начебто змінився — але чи вже вийшли з «глухого» вікна?
  if (millis() - lastEdgeMs < DEBOUNCE) return false;   // ще брязкіт — ігноруємо

  // зміна справжня: фіксуємо її й перезапускаємо вікно
  lastEdgeMs = millis();
  lastStable = raw;

  return raw;                       // true лише на фронті «розімкнено → замкнено»
}

void loop() {
  if (shockDetected()) {
    Serial.println("струс!");
    digitalWrite(PIN_LED, HIGH);
  }

  // ... тут програма робить решту справ, НЕ чекаючи на давач ...
  // напр. плавне «серцебиття» світлодіодом, опитування інших давачів, мережа
}
