#include <stdint.h>
#include <stddef.h>

#define CRC32_POLYNOMIAL 0x04C11DB7U

uint32_t crc32_bitwise(const uint8_t *data, size_t length) {
    uint32_t crc = 0xFFFFFFFFU; // Початковий стан регістра

    for (size_t i = 0; i < length; i++) {
        uint8_t byte = data[i];
        
        // Змішуємо вхідний байт у старший розряд 32-бітного регістра
        crc ^= ((uint32_t)byte << 24);

        for (int bit = 0; bit < 8; bit++) {
            if (crc & 0x80000000U) {
                // Старший біт 1: зсув та віднімання полінома через XOR
                crc = (crc << 1) ^ CRC32_POLYNOMIAL;
            } else {
                // Старший біт 0: звичайний зсув
                crc = (crc << 1);
            }
        }
    }

    return crc ^ 0xFFFFFFFFU; // Фінальний XOR
}
