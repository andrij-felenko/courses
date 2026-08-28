const uint8_t PIN_RELAY = 7;

// Уся полярність модуля живе ТУТ, в одному місці.
// active-low: увімкнути = притягнути ніжку в LOW.
const bool ACTIVE_LOW = true;

inline void relayWrite(bool on) {
    // on==true  → реле УВІМКНЕНЕ; on==false → вимкнене.
    // XOR з ACTIVE_LOW інвертує рівень лише коли модуль active-low.
    digitalWrite(PIN_RELAY, (on ^ ACTIVE_LOW) ? HIGH : LOW);
}

inline void relayOn()  { relayWrite(true);  }
inline void relayOff() { relayWrite(false); }

void setup() {
    relayOff();                     // безпечний рівень СПЕРШУ (див. крок 1)
    pinMode(PIN_RELAY, OUTPUT);
}

void loop() {
    relayOn();
    delay(1000);
    relayOff();
    delay(1000);
}
