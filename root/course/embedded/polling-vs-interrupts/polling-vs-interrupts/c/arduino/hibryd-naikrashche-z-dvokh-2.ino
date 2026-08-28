volatile unsigned long turns = 0;      // спільне з ISR → volatile

void countPulse() {                    // ISR: коротка, лише ++
  turns++;
}

void setup() {
  pinMode(SENSOR_PIN, INPUT);
  attachInterrupt(digitalPinToInterrupt(SENSOR_PIN), countPulse, RISING);
}

void loop() {
  // ... вільний для решти роботи; залізо рахує саме ...
}
