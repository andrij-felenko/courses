#include <SoftwareSerial.h>

SoftwareSerial btSerial(10, 11);   // (RX ← TXD модуля, TX → RXD модуля через дільник)

const int PIN_STATE = 7;
const int LEFT_MOTOR = 5, RIGHT_MOTOR = 6;

int  speedLevel   = 5;
bool wasConnected = false;
uint32_t lastTelemetry = 0;

void applyDrive(int leftDir, int rightDir);   // ваша реалізація моторів
float readBattery();                          // ваш давач напруги

void handleCommand(char c) {
    switch (c) {
        case 'F': applyDrive(+1, +1); break;
        case 'B': applyDrive(-1, -1); break;
        case 'L': applyDrive(-1, +1); break;
        case 'R': applyDrive(+1, -1); break;
        case 'S': applyDrive( 0,  0); break;
        default:
            if (c >= '0' && c <= '9') speedLevel = c - '0';
            break;
    }
}

void setup() {
    Serial.begin(9600);        // монітор по USB
    btSerial.begin(9600);      // модуль, РОБОЧА швидкість (не 38400 — тут не AT)
    pinMode(PIN_STATE, INPUT);
    applyDrive(0, 0);          // старт зі стопу
}

void loop() {
    // 1) команди від телефона → дії
    while (btSerial.available()) {
        handleCommand(btSerial.read());
    }

    // 2) сторож зв'язку: обрив → аварійний стоп
    bool connected = digitalRead(PIN_STATE);
    if (wasConnected && !connected) {
        applyDrive(0, 0);
        Serial.println("Зв'язок втрачено — стоп.");
    }
    wasConnected = connected;

    // 3) телеметрія раз на секунду, без блокування
    uint32_t now = millis();
    if (connected && now - lastTelemetry >= 1000) {
        lastTelemetry = now;
        btSerial.print("BAT:");
        btSerial.print(readBattery(), 2);
        btSerial.print(" SPD:");
        btSerial.print(speedLevel);
        btSerial.print("\r\n");
    }
}
