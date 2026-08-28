const uint8_t  PIN_S    = 2;
const uint8_t  N_SLOTS  = 20;
const uint32_t GUARD_US = 800;
const uint32_t WINDOW_MS = 1000;      // вікно вимірювання, мс

volatile uint32_t pulses   = 0;
volatile uint32_t lastEdge = 0;

void onEdge() {
  uint32_t t = micros();
  if (t - lastEdge >= GUARD_US) { pulses++; lastEdge = t; }
}

void setup() {
  pinMode(PIN_S, INPUT);
  Serial.begin(115200);
  const uint8_t BLOCKED = HIGH;               // з калібрування
  int edge = (BLOCKED == HIGH) ? RISING : FALLING;
  attachInterrupt(digitalPinToInterrupt(PIN_S), onEdge, edge);
}

void loop() {
  static uint32_t tWin  = 0;
  static uint32_t pPrev = 0;
  uint32_t now = millis();

  if (now - tWin >= WINDOW_MS) {
    uint32_t dt = now - tWin;                 // фактичний час вікна, мс (≈WINDOW_MS)
    tWin = now;

    noInterrupts();
    uint32_t p = pulses;
    interrupts();

    uint32_t dp = p - pPrev;                  // приріст імпульсів за вікно
    pPrev = p;

    // об/хв = 60000 · dp / (N · dt);  60000 бо dt у мс
    float rpm = 60000.0 * (float)dp / ((float)N_SLOTS * (float)dt);
    Serial.print("швидкість: ");
    Serial.print(rpm, 0);
    Serial.println(" об/хв");
  }
}
