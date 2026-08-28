#include <stdint.h>
#include <stddef.h>

/* Еталонний бітовий CRC-8, поліном 0x07 (нормальний запис, старший біт зліва).
 * init/xorout — частина профілю; для «голого» CRC-8/0x07 обидва нулі.
 * Для CRC-16/32 змінюються лише типи, маска старшого біта (0x8000 / 0x80000000)
 * і домішування байта у ВЕРХНІЙ байт: crc ^= (uint16_t)byte << 8 тощо. */
uint8_t crc8_bitwise(const uint8_t *data, size_t len,
                     uint8_t init, uint8_t xorout)
{
    uint8_t crc = init;
    for (size_t i = 0; i < len; i++) {
        crc ^= data[i];                       /* домішуємо байт у верх регістру */
        for (int bit = 0; bit < 8; bit++) {
            if (crc & 0x80)                   /* старший біт == 1 → «дільник вліз» */
                crc = (uint8_t)((crc << 1) ^ 0x07);
            else
                crc = (uint8_t)(crc << 1);    /* приведення до uint8_t = маска width */
        }
    }
    return crc ^ xorout;                       /* фінальний штрих */
}
