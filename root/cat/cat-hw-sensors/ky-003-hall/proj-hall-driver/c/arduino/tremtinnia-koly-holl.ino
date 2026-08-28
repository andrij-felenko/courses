const uint32_t DEBOUNCE_US = 1000;   // менший за найкоротший реальний період оберту

volatile uint32_t pulses   = 0;
volatile uint32_t lastEdge = 0;

void onPulse() {
    uint32_t now = micros();
    if (now - lastEdge < DEBOUNCE_US) return;  // надто рано → тремтіння, ігноруємо
    lastEdge = now;
    pulses++;
}
