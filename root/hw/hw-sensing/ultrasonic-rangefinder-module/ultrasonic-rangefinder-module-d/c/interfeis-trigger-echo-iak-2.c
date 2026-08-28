volatile uint32_t echoStart = 0;     // мить фронту
volatile uint32_t echoWidth = 0;     // готова ширина, мкс
volatile bool     echoReady = false; // новий результат є

void echoISR(void) {                 // переривання на ОБИДВА фронти echo
    if (digitalRead(ECHO_PIN)) {     // фронт — почався політ
        echoStart = micros();
    } else {                         // спад — відлуння прийшло
        echoWidth = micros() - echoStart;
        echoReady = true;
    }
}

void start_ping(void) {              // лише «пнути» — і одразу вийти
    digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
}

// у головному циклі:
//   start_ping();  ... робимо інші справи ...
//   if (echoReady) { float cm = echoWidth / 58.0f; echoReady = false; }
