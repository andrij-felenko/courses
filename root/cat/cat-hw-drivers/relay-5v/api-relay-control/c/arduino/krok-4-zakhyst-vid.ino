const uint8_t PIN_BTN   = 2;      // кнопка між ніжкою і землею
const uint8_t PIN_RELAY = 7;

const bool ACTIVE_LOW = true;
inline void relayWrite(bool on) {
    digitalWrite(PIN_RELAY, (on ^ ACTIVE_LOW) ? HIGH : LOW);
}

bool          relayState  = false;    // логічний стан реле, який перемикаємо
bool          lastReading = HIGH;     // попереднє СИРЕ читання кнопки (спокій = HIGH)
bool          btnStable   = HIGH;     // стан, у який кнопка вже устоялась
unsigned long lastEdge    = 0;        // коли сире читання востаннє смикнулось
const unsigned long DEBOUNCE_MS = 25; // «тиша» довша за деренчання (кілька мс)

void setup() {
    relayWrite(false);
    pinMode(PIN_RELAY, OUTPUT);
    pinMode(PIN_BTN, INPUT_PULLUP);   // спокій = HIGH, натиск замикає в LOW
}

void loop() {
    bool reading = digitalRead(PIN_BTN);

    if (reading != lastReading) {     // сире читання смикнулось — перезапуск відліку
        lastEdge = millis();
        lastReading = reading;
    }

    // Читання протрималось довше за DEBOUNCE і це НОВИЙ устояний стан?
    if ((millis() - lastEdge) > DEBOUNCE_MS && reading != btnStable) {
        btnStable = reading;
        if (btnStable == LOW) {       // саме натиск (не відпускання)
            relayState = !relayState; // один клац кнопки = одне перемикання реле
            relayWrite(relayState);
        }
    }
}
