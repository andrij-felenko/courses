volatile uint32_t pulses = 0;          // спільний лічильник — тому volatile

void IRAM_ATTR onPulse() {             // короткий обробник, у RAM
  pulses++;                            // лише рахуємо — і все
}

void setup() {
  pinMode(SENSOR, INPUT_PULLUP);
  attachInterrupt(digitalPinToInterrupt(SENSOR), onPulse, FALLING);
}

void loop() {
  static uint32_t last = 0;
  if (millis() - last >= 1000) {       // раз на секунду
    last = millis();
    noInterrupts();                    // безпечно зняти спільне значення
    uint32_t n = pulses; pulses = 0;
    interrupts();
    Serial.println(n);                 // друк — у loop(), НЕ в обробнику
  }
}
