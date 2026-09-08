/* ============================================================================
   krok-2-isolated-heartbeat.ino — Моніторинг сигналу оптопари (Heartbeat)
   ========================================================================== */

const uint8_t PIN_HEARTBEAT_IN = 2; // Пін з підтримкою переривань
volatile unsigned long g_last_pulse_ms = 0;

void onHeartbeatPulse() {
    g_last_pulse_ms = millis();
}

bool isIsolatedPowerOk() {
    return (millis() - g_last_pulse_ms) <= 60; // 60 мс таймаут
}

void setup() {
    Serial.begin(115200);
    pinMode(PIN_HEARTBEAT_IN, INPUT_PULLUP);
    attachInterrupt(digitalPinToInterrupt(PIN_HEARTBEAT_IN), onHeartbeatPulse, FALLING);
}

void loop() {
    static unsigned long last_check = 0;
    if (millis() - last_check >= 100) {
        last_check = millis();
        if (!isIsolatedPowerOk()) {
            Serial.println(F("⚠ [FAULT] Вторинне живлення B0505S відсутнє!"));
        }
    }
}
