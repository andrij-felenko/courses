#include <Arduino.h>

enum class DriverState {
    InitAt,
    CheckWifi,
    ConnectSocket,
    Connected,
    RecoverSoft,
    RecoverHard
};

class SessionManager {
public:
    DriverState state = DriverState::InitAt;
    uint32_t lastActivityMs = 0;
    uint8_t retryCount = 0;
    const uint8_t rstPin;

    SessionManager(uint8_t pin) : rstPin(pin) {}

    void begin(uint32_t now) {
        pinMode(rstPin, OUTPUT);
        digitalWrite(rstPin, HIGH);
        state = DriverState::InitAt;
        lastActivityMs = now;
    }

    void poll(uint32_t now) {
        uint32_t elapsed = now - lastActivityMs;

        switch (state) {
            case DriverState::Connected:
                if (elapsed > 15000) {
                    state = DriverState::RecoverSoft;
                    lastActivityMs = now;
                }
                break;

            case DriverState::RecoverSoft:
                if (elapsed > 3000) {
                    state = DriverState::RecoverHard;
                    lastActivityMs = now;
                    retryCount++;
                    digitalWrite(rstPin, LOW);
                }
                break;

            case DriverState::RecoverHard:
                if (elapsed > 100) {
                    digitalWrite(rstPin, HIGH);
                }
                if (elapsed > 2000) {
                    state = DriverState::InitAt;
                    lastActivityMs = now;
                }
                break;

            default:
                break;
        }
    }

    void handleAsyncEvent(const String& evt, uint32_t now) {
        lastActivityMs = now;
        if (state == DriverState::Connected) {
            if (evt.indexOf("CLOSED") >= 0 || evt.indexOf("WIFI DISCONNECT") >= 0) {
                state = DriverState::ConnectSocket;
            }
        }
    }
};
