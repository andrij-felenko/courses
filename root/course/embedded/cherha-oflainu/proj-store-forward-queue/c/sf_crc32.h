/* sf_crc32.h — CRC-32 за IEEE 802.3 у відображеній (reflected) формі.
 *
 * Той самий поліном, що в Ethernet, ZIP і gzip: 0x04C11DB7, записаний
 * задом наперед як 0xEDB88320. Початкове значення 0xFFFFFFFF, фінальне
 * інвертування. Саме цей варіант очікує сервер на іншому кінці радіо,
 * тож відступати від нього не можна.
 */
#ifndef SF_CRC32_H
#define SF_CRC32_H

#include <stddef.h>
#include <stdint.h>

#define SF_CRC32_INIT 0xFFFFFFFFu

/* Потокова форма: дозволяє рахувати суму по шматках, не збираючи
 * увесь запис у безперервний буфер. */
uint32_t sf_crc32_update(uint32_t crc, const void *data, size_t len);
uint32_t sf_crc32_final(uint32_t crc);

/* Разова форма для суцільного буфера. */
uint32_t sf_crc32(const void *data, size_t len);

#endif /* SF_CRC32_H */
