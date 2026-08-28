volatile unsigned long pulses = 0;     // лічить ISR, читає loop()

void IRAM_ATTR onPulse() { pulses++; }  // ISR: коротко — лише інкремент

void loop() {
    noInterrupts();
    unsigned long p = pulses;           // знімок цілого 32-бітного значення
    interrupts();
    // далі працюємо з копією p, а не з живою pulses
}
