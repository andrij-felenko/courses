// Логіка атомарного оновлення конфігуратора завантажувача
#include <Arduino.h>

struct BootConfig {
    uint8_t activeSlot; // 0 для user1.bin, 1 для user2.bin
    uint32_t checksum;
};

bool updateBootSector(uint8_t newSlot, uint32_t newChecksum) {
    BootConfig config;
    config.activeSlot = newSlot;
    config.checksum = newChecksum;

    // Скидання та атомарний запис конфігураційного сектора 0x0C000
    if (ESP.flashEraseSector(0x0C000 / SPI_FLASH_SEC_SIZE)) {
        return ESP.flashWrite(0x0C000, reinterpret_cast<uint32_t*>(&config), sizeof(config));
    }
    return false;
}
