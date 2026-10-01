#include <stdint.h>
#include <stdbool.h>

// Розрахунок XOR контрольної суми сегментів образу
uint8_t calculate_xor_checksum(const uint8_t *data, uint32_t length) {
    uint8_t checksum = 0xEF; // Початкове значення маски Espressif
    for (uint32_t i = 0; i < length; i++) {
        checksum ^= data[i];
    }
    return checksum;
}

// Перевірка цілісності слота FOTA
bool verify_fota_slot(uint32_t flash_offset, uint8_t expected_checksum) {
    // Зчитування даних із флеш-пам'яті та порівняння контрольної суми
    uint8_t computed = calculate_xor_checksum((const uint8_t*)flash_offset, 1024);
    return (computed == expected_checksum);
}
