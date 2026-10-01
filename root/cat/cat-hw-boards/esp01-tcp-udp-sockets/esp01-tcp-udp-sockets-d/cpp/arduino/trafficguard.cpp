#include <Arduino.h>

class TrafficGuard {
private:
    unsigned long lastSendMs = 0;
    const unsigned long minIntervalMs = 200; // Максимум 5 пакетів на секунду

public:
    bool canSend(unsigned long nowMs) {
        if (nowMs - lastSendMs < minIntervalMs) {
            return false;
        }
        lastSendMs = nowMs;
        return true;
    }

    uint8_t computeChecksum(const uint8_t* payload, size_t len) {
        uint8_t crc = 0;
        for (size_t i = 0; i < len; i++) {
            crc ^= payload[i];
        }
        return crc;
    }
};
