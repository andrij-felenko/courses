const uint8_t PIN_SW     = 2;
const uint8_t PIN_LED    = 13;
const uint8_t ACTIVE     = LOW;
const uint16_t DEBOUNCE  = 40;         // глухе вікно проти брязкоту, мс
const uint16_t WINDOW    = 1000;       // вікно підрахунку, мс
const uint8_t  THRESHOLD = 5;          // поріг «сильної вібрації» за вікно

bool     lastStable = false;
uint32_t lastEdgeMs = 0;

uint16_t count      = 0;               // струсів у поточному вікні
uint32_t windowMs   = 0;               // початок поточного вікна

bool shockDetected() {                 // той самий неблокувальний дебаунс
  bool raw = (digitalRead(PIN_SW) == ACTIVE);
  if (raw == lastStable) return false;
  if (millis() - lastEdgeMs < DEBOUNCE) return false;
  lastEdgeMs = millis();
  lastStable = raw;
  return raw;                          // true лише на замиканні
}

void setup() {
  pinMode(PIN_SW, INPUT_PULLUP);
  pinMode(PIN_LED, OUTPUT);
  Serial.begin(115200);
  windowMs = millis();
}

void loop() {
  // 1) лічимо підтверджені струси
  if (shockDetected()) count++;

  // 2) щойно вікно (1 с) вичерпалось — оцінюємо й починаємо нове
  if (millis() - windowMs >= WINDOW) {
    Serial.print("струсів за секунду: ");
    Serial.println(count);

    digitalWrite(PIN_LED, count >= THRESHOLD ? HIGH : LOW);   // тривога?

    count    = 0;                      // скидаємо лічильник
    windowMs = millis();               // нове вікно
  }
}
