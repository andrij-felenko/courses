const uint8_t  PIN_S    = 2;
const uint8_t  N_SLOTS  = 20;
const uint32_t GUARD_US = 800;

volatile uint32_t period   = 0;       // останній період між фронтами, мкс
volatile uint32_t lastEdge = 0;
volatile bool     fresh    = false;   // прапорець «є новий вимір»

void onEdge() {
  uint32_t t = micros();
  uint32_t dt = t - lastEdge;         // проміжок від попереднього фронту
  if (dt >= GUARD_US) {               // мертвий час: відкидаємо дрижання
    period   = dt;                    // ← ось воно, T у мікросекундах
    lastEdge = t;
    fresh    = true;
  }
}

void setup() {
  pinMode(PIN_S, INPUT);
  Serial.begin(115200);
  const uint8_t BLOCKED = HIGH;
  int edge = (BLOCKED == HIGH) ? RISING : FALLING;
  attachInterrupt(digitalPinToInterrupt(PIN_S), onEdge, edge);
}

void loop() {
  if (fresh) {
    noInterrupts();
    uint32_t T = period;              // знімок періоду, мкс
    fresh = false;
    interrupts();

    // об/хв = 60 000 000 / (N · T);  60e6 бо T у мкс
    float rpm = 60000000.0 / ((float)N_SLOTS * (float)T);
    Serial.print("миттєво: ");
    Serial.print(rpm, 0);
    Serial.println(" об/хв");
  }
}
