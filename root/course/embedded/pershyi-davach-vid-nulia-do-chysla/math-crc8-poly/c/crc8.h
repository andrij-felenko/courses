#ifndef CRC8_H
#define CRC8_H

#include <stdbool.h>
#include <stddef.h>
#include <stdint.h>

/* Генераторний поліном G(x) = x^8 + x^5 + x^4 + 1.
   Старший біт x^8 у восьмибітному регістрі не зберігаємо — лишається 0x31. */
#define CRC8_POLY 0x31u

/* Початковий стан регістра для сенсорів Sensirion SHT3x/SHT4x. */
#define CRC8_INIT 0xFFu

/* Побітовий автомат: вісім тактів зсуву зі зворотним зв'язком на кожен байт. */
uint8_t crc8_bitwise(const uint8_t *data, size_t len);

/* Заповнює масив на 256 елементів — залишок від проходу кожного
   можливого значення байта через вісім тактів. */
void crc8_build_table(uint8_t table[256]);

/* Спільна таблиця модуля; будується під час першого звертання. */
const uint8_t *crc8_table(void);

/* Табличний розрахунок: один XOR і одне читання з пам'яті на байт. */
uint8_t crc8_fast(const uint8_t *data, size_t len);

/* Кадр = дані + байт CRC у кінці. Прогін усього кадру дає нульовий залишок. */
bool crc8_frame_ok(const uint8_t *frame, size_t len);

/* Один байт крізь вісім тактів із записом проміжних станів у steps[8]
   (steps може бути NULL). Повертає стан регістра після байта. */
uint8_t crc8_byte_trace(uint8_t reg, uint8_t data, uint8_t steps[8]);

/* Розбирає трибайтний кадр SHT3x (старший байт, молодший байт, CRC).
   0 — слово покладено в *out; -1 — кадр биті або аргументи невалідні. */
int crc8_sht3x_word(const uint8_t *frame, size_t len, uint16_t *out);

#endif /* CRC8_H */
