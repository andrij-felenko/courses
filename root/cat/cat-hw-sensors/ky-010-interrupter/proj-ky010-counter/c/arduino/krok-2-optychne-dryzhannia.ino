const uint32_t GUARD_US = 800;    // мертвий час, мкс: більший за пачку, менший за період

volatile uint32_t pulses  = 0;
volatile uint32_t lastEdge = 0;   // мітка часу останнього ЗАРАХОВАНОГО фронту, мкс

void onEdge() {
  uint32_t t = micros();          // micros() безпечний в ISR (лише читає лічильник)
  if (t - lastEdge >= GUARD_US) { // пройшло досить від попереднього фронту?
    pulses++;
    lastEdge = t;
  }
  // інакше — це дрижання того ж зубця, ігноруємо
}
