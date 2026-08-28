volatile uint32_t pulses = 0;          // volatile — свіжість значення

void IRAM_ATTR onPulse() { pulses++; } // обробник лише рахує

void loop() {
  noInterrupts();                      // ← критична секція: цілісно
  uint32_t n = pulses;                 //   «знімок» спільних даних
  pulses = 0;
  interrupts();                        // ← переривання знову ввімкнені
  // ... далі працюємо з локальним n, поза секцією ...
  Serial.println(n);                   // повільний друк — НЕ в секції
}
