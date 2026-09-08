/* ============================================================================
   krok-3-isolated-uart.ino — Безпечний вивід у UART через ізолятор
   ========================================================================== */

extern bool isIsolatedPowerOk();

void sendIsolatedMessage(const char *msg) {
    if (!isIsolatedPowerOk()) {
        Serial.println(F("[UART Blocked] Передачу заблоковано: відсутнє живлення вторинного домену"));
        return;
    }

    // Відправка на апаратний UART, з'єднаний з цифровим ізолятором (ADuM1201)
    Serial1.println(msg);
}

void setup() {
    Serial.begin(115200);
    Serial1.begin(9600);
}

void loop() {
    delay(1000);
    sendIsolatedMessage("PING_ISOLATED_DEVICE");
}
