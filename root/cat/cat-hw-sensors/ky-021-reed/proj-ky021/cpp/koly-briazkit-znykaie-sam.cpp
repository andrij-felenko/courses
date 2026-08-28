const uint8_t PIN_REED = 2;              // на Uno INT-входи — D2 і D3
const unsigned long DEBOUNCE_MS = 10;

volatile unsigned long revolutions = 0;  // змінюється в перериванні → volatile
volatile unsigned long lastEdgeMs  = 0;

void onReedFall() {                       // обробник переривання (ISR)
  unsigned long now = millis();           // millis() всередині ISR читати можна
  if (now - lastEdgeMs >= DEBOUNCE_MS) {  // той самий таймерний дебаунс
    revolutions++;
    lastEdgeMs = now;
  }
}

void setup() {
  pinMode(PIN_REED, INPUT);
  // край HIGH→LOW (магніт з'явився) смикає onReedFall()
  attachInterrupt(digitalPinToInterrupt(PIN_REED), onReedFall, FALLING);
  Serial.begin(9600);
}

void loop() {
  static unsigned long lastReport = 0;
  if (millis() - lastReport >= 1000) {
    lastReport = millis();
    noInterrupts();                        // читаємо 32-бітну лічбу атомарно
    unsigned long snapshot = revolutions;
    interrupts();
    Serial.print("обертів: ");
    Serial.println(snapshot);
  }
}
