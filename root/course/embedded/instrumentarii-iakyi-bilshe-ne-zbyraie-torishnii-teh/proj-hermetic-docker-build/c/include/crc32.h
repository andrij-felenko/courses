/* CRC-32 (IEEE 802.3, поліном 0xEDB88320) для перевірки цілісності образу
   прямо в прошивці. Табличка на 16 входів замість 256: у Flash вона коштує
   64 байти, а швидкості для одноразової перевірки при старті вистачає. */
#ifndef CRC32_H
#define CRC32_H

#include <stddef.h>
#include <stdint.h>

#define CRC32_INIT 0xFFFFFFFFU

/* Продовжує рахунок над черговим шматком. NULL або нульова довжина —
   не помилка: crc повертається незмінним, щоб виклик у циклі не обростав
   перевірками на боці викликача. */
uint32_t crc32_update(uint32_t crc, const void *data, size_t len);

/* Фінальне інвертування: те саме значення, що дає zlib.crc32 у Python,
   тож образ, підписаний stamp_meta.py, сходиться з розрахунком у прошивці. */
static inline uint32_t crc32_final(uint32_t crc)
{
    return crc ^ 0xFFFFFFFFU;
}

#endif /* CRC32_H */
