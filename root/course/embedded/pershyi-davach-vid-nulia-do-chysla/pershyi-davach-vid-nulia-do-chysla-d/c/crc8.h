#ifndef SHT3X_CRC8_H
#define SHT3X_CRC8_H

/* CRC-8 у варіанті Sensirion: поліном 0x31 (x^8 + x^5 + x^4 + 1),
   початкове значення 0xFF, без відображення вхідних і вихідних бітів,
   фінальний XOR 0x00. Тими самими параметрами рахує апаратний автомат
   усередині сенсора, тому наш результат мусить збігтися байт у байт. */

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

#define SHT3X_CRC8_POLYNOMIAL 0x31u
#define SHT3X_CRC8_INIT       0xFFu

/* Контрольна сума довільного буфера. */
uint8_t sht3x_crc8(const uint8_t *data, size_t len);

/* Перевірка одного 16-бітного слова кадру проти переданого сенсором байта. */
bool sht3x_crc8_check(const uint8_t word[2], uint8_t expected);

#endif /* SHT3X_CRC8_H */
