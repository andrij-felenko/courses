#include <stdint.h>
#include <stdbool.h>
#include <stddef.h>

/* 64-бітна пріоритетна бітова черга */
typedef struct {
    uint64_t mask;           /* Бітова маска активних рівнів (розряди 0..63) */
    size_t   count;          /* Загальна кількість елементів у всіх чергах */
} BitQueue64;

/* 128-бітна розширена пріоритетна бітова черга */
typedef struct {
    uint64_t words[2];       /* words[0] — рівні 0..63, words[1] — рівні 64..127 */
    size_t   count;          /* Сумарна кількість елементів у системі */
} BitQueue128;
