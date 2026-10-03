#include <Arduino.h>

enum class DriverState {
    InitAt,
    SetCwMode,
    SetCipMux,
    Connecting,
    Connected,
    WaitPrompt,
    WaitSendOk,
    Recovery
};

class Esp01SocketDriver {
public:
    Esp01SocketDriver(uint8_t resetPin)
        : m_resetPin(resetPin), m_state(DriverState::InitAt),
          m_stateTimer(0), m_retryCount(0), m_txData(nullptr), m_txLen(0) {}

    void begin() {
        pinMode(m_resetPin, OUTPUT);
        digitalWrite(m_resetPin, HIGH);
        resetToInit();
    }

    void sendPacket(const uint8_t* data, size_t len) {
        if (m_state != DriverState::Connected) return;
        m_txData = data;
        m_txLen = len;
        m_state = DriverState::WaitPrompt;
        m_stateTimer = millis();

        char cmd[32];
        snprintf(cmd, sizeof(cmd), "AT+CIPSEND=0,%u", (unsigned int)len);
        sendCmd(cmd);
    }

    void onParserOk() {
        switch (m_state) {
            case DriverState::InitAt:
                m_state = DriverState::SetCwMode;
                sendCmd("AT+CWMODE=1");
                break;
            case DriverState::SetCwMode:
                m_state = DriverState::SetCipMux;
                sendCmd("AT+CIPMUX=1");
                break;
            case DriverState::SetCipMux:
                m_state = DriverState::Connecting;
                sendCmd("AT+CIPSTART=0,\"TCP\",\"192.168.1.100\",8080");
                break;
            case DriverState::Connecting:
                m_state = DriverState::Connected;
                m_retryCount = 0;
                break;
            default:
                break;
        }
    }

    void onPrompt() {
        if (m_state == DriverState::WaitPrompt && m_txData != nullptr) {
            Serial.write(m_txData, m_txLen);
            m_state = DriverState::WaitSendOk;
            m_stateTimer = millis();
        }
    }

    void onSendOk() {
        if (m_state == DriverState::WaitSendOk) {
            m_state = DriverState::Connected;
            m_stateTimer = millis();
        }
    }

    void update() {
        uint32_t now = millis();
        uint32_t elapsed = now - m_stateTimer;

        switch (m_state) {
            case DriverState::InitAt:
            case DriverState::SetCwMode:
            case DriverState::SetCipMux:
                if (elapsed > 2000) {
                    if (++m_retryCount >= 3) {
                        triggerHardwareReset();
                    } else {
                        resetToInit();
                    }
                }
                break;

            case DriverState::Connecting:
                if (elapsed > 10000) {
                    resetToInit();
                }
                break;

            case DriverState::WaitPrompt:
                if (elapsed > 2000) {
                    m_state = DriverState::Connected;
                }
                break;

            case DriverState::WaitSendOk:
                if (elapsed > 5000) {
                    m_state = DriverState::Connected;
                }
                break;

            case DriverState::Recovery:
                if (elapsed > 500) {
                    resetToInit();
                }
                break;

            default:
                break;
        }
    }

private:
    void sendCmd(const char* cmd) {
        Serial.print(cmd);
        Serial.print("\r\n");
        m_stateTimer = millis();
    }

    void resetToInit() {
        m_state = DriverState::InitAt;
        m_stateTimer = millis();
        sendCmd("AT");
    }

    void triggerHardwareReset() {
        m_state = DriverState::Recovery;
        digitalWrite(m_resetPin, LOW);
        delay(100);
        digitalWrite(m_resetPin, HIGH);
        m_stateTimer = millis();
    }

    uint8_t m_resetPin;
    DriverState m_state;
    uint32_t m_stateTimer;
    uint8_t m_retryCount;
    const uint8_t* m_txData;
    size_t m_txLen;
};
