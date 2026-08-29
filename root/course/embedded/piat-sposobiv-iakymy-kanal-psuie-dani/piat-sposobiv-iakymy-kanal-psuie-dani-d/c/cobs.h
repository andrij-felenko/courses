#ifndef COBS_H
#define COBS_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

// Consistent Overhead Byte Stuffing: після кодування байт 0x00 у тілі не трапляється,
// тому його можна вживати як абсолютний роздільник меж кадру.

// Найгірший випадок кодування: один байт на кожні 254 плюс стартовий код.
size_t cobs_max_encoded(size_t len);

// Обидві функції ніколи не пишуть за межі dst_cap: декодер отримує дані з лінії,
// а там код зміщення міг бути перевернутий шумом на будь-яке значення.
bool cobs_encode(const uint8_t *src, size_t src_len,
                 uint8_t *dst, size_t dst_cap, size_t *out_len);

bool cobs_decode(const uint8_t *src, size_t src_len,
                 uint8_t *dst, size_t dst_cap, size_t *out_len);

#endif // COBS_H
