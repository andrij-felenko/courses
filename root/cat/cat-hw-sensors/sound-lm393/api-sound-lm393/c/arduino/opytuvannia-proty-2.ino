const uint8_t SOUND = 2;                 // на Uno переривання є на D2 і D3
volatile bool  hit  = false;             // прапорець «була подія», ставить ISR
volatile unsigned long hitAt = 0;        // коли саме (для дебаунсу — далі)

// ISR: обробник переривання. Коротка, без Serial і delay.
void onSound() {
    hit   = true;
    hitAt = millis();
}

void setup() {
    pinMode(SOUND, INPUT);
    // digitalPinToInterrupt переганяє номер ноги в номер переривання
    attachInterrupt(digitalPinToInterrupt(SOUND), onSound, FALLING);
    Serial.begin(9600);
}

void loop() {
    if (hit) {                           // головний цикл лише збирає врожай
        hit = false;
        Serial.println("звук (по перериванню)!");
    }
    // тут можна робити будь-що важке — переривання не проґавить фронт
}
