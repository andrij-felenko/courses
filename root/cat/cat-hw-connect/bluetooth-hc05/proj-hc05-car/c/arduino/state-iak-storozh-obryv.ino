const int PIN_STATE = 7;    // STATE модуля → цей вхід МК
bool wasConnected = false;

void setup() {
    // ...інша ініціалізація...
    pinMode(PIN_STATE, INPUT);
}

void loop() {
    // ...читання команд і телеметрія...

    bool connected = digitalRead(PIN_STATE);   // 1 = є з'єднання, 0 = немає

    if (wasConnected && !connected) {
        // зв'язок ЩОЙНО обірвався — аварійний стоп
        applyDrive(0, 0);
        Serial.println("Зв'язок втрачено — мотори зупинено.");
    }
    wasConnected = connected;
}
