#include <stdint.h>
#include <stddef.h>

uint16_t inet_checksum(const uint16_t *words, size_t n) {
    uint32_t sum = 0;
    for (size_t i = 0; i < n; i++)
        sum += words[i];                   // складаємо у 32-бітний акумулятор
    while (sum >> 16)                       // завертаємо перенос, доки він є
        sum = (sum & 0xFFFF) + (sum >> 16);
    return (uint16_t)~sum;                  // інверсія — і це вже контрольна сума
}
