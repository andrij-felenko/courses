const unsigned long PERIOD = 500;   // мс
unsigned long last = 0;
bool on = false;

void loop() {
    unsigned long now = millis();
    if (now - last >= PERIOD) {      // настав час?
        last = now;                  // оновили мітку (саме now, не millis() ще раз)
        on = !on;
        digitalWrite(LED_BUILTIN, on);
    }
    // ... тут крутиться решта коду, нічого не чекаючи ...
}
