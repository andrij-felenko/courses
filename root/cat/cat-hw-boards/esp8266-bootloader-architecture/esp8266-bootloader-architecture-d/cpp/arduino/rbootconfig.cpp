#include <Arduino.h>

struct RBootConfig {
    uint8_t magic;
    uint8_t version;
    uint8_t mode;
    uint8_t currentRom;
    uint8_t gpioRom0;
    uint8_t count;
    uint8_t bootOnce;
    uint32_t roms[4];
};

class FotaSlotManager {
public:
    static bool validateChecksum(const uint8_t* buffer, size_t length, uint8_t targetChecksum) {
        uint8_t checksum = 0xEF;
        for (size_t i = 0; i < length; ++i) {
            checksum ^= buffer[i];
        }
        return checksum == targetChecksum;
    }

    static bool prepareRollbackSwitch(RBootConfig& config, uint8_t newSlotIndex) {
        if (newSlotIndex >= config.count) {
            return false;
        }
        config.currentRom = newSlotIndex;
        config.bootOnce = 1; // Увімкнення режиму одноразової перевірки FOTA
        return true;
    }
};
