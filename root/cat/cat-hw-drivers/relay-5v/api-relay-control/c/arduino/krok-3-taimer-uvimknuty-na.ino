const uint8_t PIN_RELAY = 7;
const uint8_t RELAY_ON  = LOW;
const uint8_t RELAY_OFF = HIGH;

// Стан таймера реле.
bool          relayActive = false;   // чи реле зараз увімкнене таймером
unsigned long relayOffAt  = 0;       // МИТЬ (за millis), коли треба вимкнути

// Увімкнути реле рівно на durationMs мілісекунд.
void relayOnFor(unsigned long durationMs) {
    digitalWrite(PIN_RELAY, RELAY_ON);
    relayActive = true;
    relayOffAt  = millis() + durationMs;   // коли гасити
}

// Викликати В КОЖНОМУ проході loop(): сам вимкне, коли час вийде.
void relayTick() {
    if (relayActive && (long)(millis() - relayOffAt) >= 0) {
        digitalWrite(PIN_RELAY, RELAY_OFF);
        relayActive = false;
    }
}

void setup() {
    digitalWrite(PIN_RELAY, RELAY_OFF);
    pinMode(PIN_RELAY, OUTPUT);
    relayOnFor(5000);                 // клацнули увімкнене на 5 секунд
}

void loop() {
    relayTick();                      // стежить за часом, не блокуючи
    // ...сюди можна дописати будь-що: кнопки, давачі, індикатор —
    //    усе працює, поки реле відлічує свої 5 секунд.
}
