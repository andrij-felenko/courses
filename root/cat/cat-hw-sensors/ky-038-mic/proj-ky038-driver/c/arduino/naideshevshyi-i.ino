const uint8_t PIN_DO = 2;          // на ATmega328 переривання є на D2 і D3
volatile unsigned long soundCount = 0;
volatile unsigned long lastEventISR = 0;
const unsigned long WINDOW_MS = 300;

// ISR: якнайкоротша. Лише рахуємо подію з тим самим вікном придушення.
void onSound() {
    unsigned long now = millis();               // millis() в ISR читати можна
    if (now - lastEventISR > WINDOW_MS) {
        lastEventISR = now;
        soundCount++;
    }
}

void setup() {
    pinMode(PIN_DO, INPUT);
    Serial.begin(9600);
    delay(300);
    // Спрацьовуємо на фронт. Якщо звук на твоїй платі тягне DO у HIGH —
    // це RISING; якщо у LOW — FALLING. CHANGE ловить обидва напрями.
    attachInterrupt(digitalPinToInterrupt(PIN_DO), onSound, RISING);
}

void loop() {
    static unsigned long shown = 0;
    if (soundCount != shown) {         // друкуємо лише коли лічильник змінився
        noInterrupts();                // читаємо volatile-змінну атомарно
        unsigned long c = soundCount;
        interrupts();
        shown = c;
        Serial.print("подій: ");
        Serial.println(c);
    }
    // loop() майже вільний — уся реакція на звук живе в перериванні
}
