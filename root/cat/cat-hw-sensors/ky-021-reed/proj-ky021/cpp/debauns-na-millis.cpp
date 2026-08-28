const uint8_t PIN_REED = 2;
const unsigned long DEBOUNCE_MS = 10;   // вікно тиші після події (мс)

inline bool magnetPresent(uint8_t pin) { return digitalRead(pin) == LOW; }

unsigned long revolutions = 0;
bool          lastState   = false;      // магніт був поряд минулого разу?
unsigned long lastEdgeMs  = 0;          // коли востаннє зарахували край
unsigned long lastReport  = 0;

void setup() {
  pinMode(PIN_REED, INPUT);
  Serial.begin(9600);
}

void loop() {
  unsigned long now = millis();
  bool state = magnetPresent(PIN_REED);

  // цікавить перехід «не було → з'явився» (край HIGH→LOW),
  // і лише якщо від минулого зарахованого краю минуло вікно тиші
  if (state && !lastState && (now - lastEdgeMs) >= DEBOUNCE_MS) {
    revolutions++;
    lastEdgeMs = now;
  }
  lastState = state;

  if (now - lastReport >= 1000) {
    lastReport = now;
    Serial.print("обертів: ");
    Serial.println(revolutions);
  }
}
