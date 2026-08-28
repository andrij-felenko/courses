const uint8_t PIN_SW = 4;
const uint16_t DEBOUNCE = 40;          // глухе вікно, мс

volatile bool     shockFlag  = false;
volatile uint32_t lastIsrMs  = 0;

void IRAM_ATTR isrShock() {
  uint32_t now = millis();             // у сучасних ядрах ESP32 millis() в ISR безпечний (він у IRAM)
  if (now - lastIsrMs < DEBOUNCE) return;   // ще брязкіт тієї ж події — ігноруємо
  lastIsrMs = now;
  shockFlag = true;
}
