#ifndef CRC32_H
#define CRC32_H

#include <stddef.h>
#include <stdint.h>

/*
 * CRC-32/IEEE (поліном 0xEDB88320, віддзеркалений), той самий, що в zip і Ethernet.
 * Використовують два місця: заголовок маніфесту і сторінка стану завантаження.
 */
uint32_t crc32_ieee(const uint8_t *data, size_t length);

#endif /* CRC32_H */
