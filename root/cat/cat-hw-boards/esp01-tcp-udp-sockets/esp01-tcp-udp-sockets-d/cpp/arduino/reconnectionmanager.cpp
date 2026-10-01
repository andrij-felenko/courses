#include <Arduino.h>

class ReconnectionManager {
public:
    ReconnectionManager(HardwareSerial &serial) 
        : _serial(serial), _delayMs(1000), _maxDelayMs(60000), _lastAttempt(0) {}

    void update() {
        if (millis() - _lastAttempt >= _delayMs) {
            _lastAttempt = millis();

            if (!checkStatus()) {
                reconnect();
                _delayMs = min(_delayMs * 2, _maxDelayMs);
            } else {
                _delayMs = 1000;
            }
        }
    }

private:
    HardwareSerial &_serial;
    unsigned long _delayMs;
    const unsigned long _maxDelayMs;
    unsigned long _lastAttempt;

    bool checkStatus() {
        _serial.print("AT+CIPSTATUS\r\n");
        // Логіка зчитування OK/STATUS
        return true; 
    }

    void reconnect() {
        _serial.print("AT+CIPSTART=\"TCP\",\"192.168.1.100\",8080\r\n");
    }
};
