#include <stdint.h>
#include <stddef.h>

uint16_t internet_checksum(const uint8_t *data, size_t len) {
    uint32_t sum = 0;

    // Складаємо дані по два байти — як 16-бітні слова.
    while (len > 1) {
        sum += ((uint32_t)data[0] << 8) | data[1];
        data += 2;
        len  -= 2;
    }
    if (len)                        // непарний «хвіст» доповнюємо нулем справа
        sum += (uint32_t)data[0] << 8;

    while (sum >> 16)               // загортаємо перенос, поки він є
        sum = (sum & 0xFFFF) + (sum >> 16);

    return (uint16_t)~sum;          // інверсія — і є контрольне число
}
