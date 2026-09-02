/* fnv1a.h — 64-бітний некриптографічний хеш Fowler–Noll–Vo (FNV-1a).
 *
 * Модуль навмисно нічого не знає про gawk: це чиста функція, яку можна
 * перевірити окремо від інтерпретатора. Уся прив'язка до API — у fast_tools.c.
 */
#ifndef FNV1A_H
#define FNV1A_H

#include <stddef.h>
#include <stdint.h>

/* "0x" + 16 шістнадцяткових цифр + термінальний нуль. */
#define FNV1A_HEX_SIZE 19

/* Хеш len байтів за адресою data. Порожній вхід законний: повертається базис. */
uint64_t fnv1a_64(const void *data, size_t len);

/* Записує хеш у buf як "0x%016x". Повертає кількість записаних символів
   (без термінального нуля) або -1, якщо буфер замалий. */
int fnv1a_64_hex(uint64_t hash, char *buf, size_t size);

#endif /* FNV1A_H */
