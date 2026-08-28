const uint8_t  SOL_PIN  = 5;
const uint16_t PULSE_MS = 60;

bool     solOn      = false;   // чи зараз соленоїд під струмом
uint32_t solStart   = 0;       // мить увімкнення (millis)

void solenoidStart() {         // почати клацання — не чекаючи його кінця
    digitalWrite(SOL_PIN, HIGH);
    solOn    = true;
    solStart = millis();
}

void solenoidUpdate() {        // кликати щоразу в loop(): вимкне, коли настане час
    if (solOn && (millis() - solStart >= PULSE_MS)) {
        digitalWrite(SOL_PIN, LOW);
        solOn = false;
    }
}

void loop() {
    // ... читаємо кнопки, крутимо логіку, миготимо світлом ...
    if (buttonPressed())
        solenoidStart();       // клац — і одразу далі, без застигання
    solenoidUpdate();          // а вимкнеться саме собою за 60 мс
    // ... решта loop() крутиться весь час, соленоїд їй не заважає ...
}
