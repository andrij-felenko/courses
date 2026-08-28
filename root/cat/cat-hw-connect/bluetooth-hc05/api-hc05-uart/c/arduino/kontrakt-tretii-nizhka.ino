const int PIN_STATE = 7;    // STATE модуля → цей вхід МК
bool wasConnected = false;

void setup() {
    // ...інша ініціалізація...
    pinMode(PIN_STATE, INPUT);
}

void loop() {
    bool connected = digitalRead(PIN_STATE);   // 1 = є з'єднання, 0 = немає

    if (!wasConnected && connected) {          // 0→1: напарник щойно під'єднався
        Serial.println("З'єднання встановлено.");
    }
    if (wasConnected && !connected) {          // 1→0: зв'язок щойно обірвався
        Serial.println("Зв'язок втрачено.");
    }
    wasConnected = connected;
}
