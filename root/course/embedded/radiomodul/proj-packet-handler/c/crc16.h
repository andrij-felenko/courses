#ifndef CRC16_H
#define CRC16_H

#include <stddef.h>
#include <stdint.h>

/* CRC-16/CCITT-FALSE: x^16 + x^12 + x^5 + 1, Init = 0xFFFF, без фінального XOR.
   Саме цей варіант рахує апаратний блок CRC у CC1101, nRF24 і SX126x. */
#define CRC16_POLY 0x1021u
#define CRC16_INIT 0xFFFFu

/* Домішує один байт до поточного залишку. Байт заходить старшим бітом
   уперед — у тому ж порядку, у якому він піде в ефір. */
uint16_t crc16_update(uint16_t crc, uint8_t byte);

/* Сума цілого блоку з чистого початкового значення. */
uint16_t crc16_block(const uint8_t *data, size_t len);

#endif /* CRC16_H */
