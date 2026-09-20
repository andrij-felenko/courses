#ifndef EEPROM_DRIVER_H
#define EEPROM_DRIVER_H

#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>
#include <string.h>

#define EEPROM_SIZE_BYTES 512

// Проста емуляція апаратного блоку EEPROM у пам'яті
static uint8_t g_simulated_eeprom[EEPROM_SIZE_BYTES];

static inline bool eeprom_write_block(uint32_t address, const uint8_t *buffer, size_t length) {
    if (!buffer || (address + length) > EEPROM_SIZE_BYTES) {
        return false;
    }
    memcpy(&g_simulated_eeprom[address], buffer, length);
    return true;
}

static inline bool eeprom_read_block(uint32_t address, uint8_t *buffer, size_t length) {
    if (!buffer || (address + length) > EEPROM_SIZE_BYTES) {
        return false;
    }
    memcpy(buffer, &g_simulated_eeprom[address], length);
    return true;
}

#endif // EEPROM_DRIVER_H
