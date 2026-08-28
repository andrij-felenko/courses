const uint8_t  SOL_PIN   = 5;
const uint16_t PULSE_MS  = 60;     // тривалість самого клацання
const uint16_t REARM_MS  = 200;    // мертвий час: раніше — не клацаємо повторно

bool     solOn      = false;
uint32_t solStart   = 0;
uint32_t solLastEnd = 0;           // коли завершилося останнє клацання

// повертає true, якщо клацання прийнято; false — якщо відкинуто (ще рано)
bool solenoidTryFire() {
    if (solOn) return false;                          // уже клацаємо — не чіпати
    if (millis() - solLastEnd < REARM_MS) return false; // ще не перезарядилися
    digitalWrite(SOL_PIN, HIGH);
    solOn    = true;
    solStart = millis();
    return true;
}

void solenoidUpdate() {
    if (solOn && (millis() - solStart >= PULSE_MS)) {
        digitalWrite(SOL_PIN, LOW);
        solOn      = false;
        solLastEnd = millis();     // запускаємо відлік перезарядки
    }
}
