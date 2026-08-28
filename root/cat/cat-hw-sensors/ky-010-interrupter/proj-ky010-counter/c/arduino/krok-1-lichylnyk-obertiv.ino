const uint8_t PIN_S   = 2;        // сигнал KY-010; D2 і D3 на Uno — входи переривання
const uint8_t N_SLOTS = 20;       // прорізів на диску (стільки імпульсів = 1 оберт)

volatile uint32_t pulses = 0;     // лічильник імпульсів; його чіпає ISR → тільки volatile

void onEdge() {                   // ISR: коротка, без Serial, без delay
  pulses++;
}

void setup() {
  pinMode(PIN_S, INPUT);
  Serial.begin(115200);
  attachInterrupt(digitalPinToInterrupt(PIN_S), onEdge, RISING);
}

void loop() {
  static uint32_t tPrint = 0;
  uint32_t now = millis();
  if (now - tPrint >= 1000) {     // раз на секунду знімаємо зріз
    tPrint = now;

    noInterrupts();               // атомарно зчитуємо 32-бітне значення
    uint32_t p = pulses;
    interrupts();

    uint32_t revs = p / N_SLOTS;  // цілих обертів від старту
    Serial.print("обертів усього: ");
    Serial.println(revs);
  }
}
