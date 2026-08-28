/* pmlog.c — кільцевий журнал на файлі з прямим звертанням.
   збірка:  cc -O2 -mclwb -o pmlog pmlog.c                          */
#define _GNU_SOURCE
#include <errno.h>
#include <fcntl.h>
#include <immintrin.h>
#include <stddef.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>
#include <sys/mman.h>
#include <unistd.h>

#define LINE   64u          /* рядок кешу */
#define SLOT   4096u        /* слот = сторінка */
#define SLOTS  1024u        /* 4 МіБ журналу */

struct slot {
    uint64_t commit;        /* 0 — порожньо; інакше номер запису + 1 */
    uint32_t len;
    uint32_t crc;
    uint8_t  body[SLOT - 16];
};
_Static_assert(sizeof(struct slot) == SLOT, "слот мусить дорівнювати сторінці");
_Static_assert(offsetof(struct slot, commit) % 8 == 0, "ознака мусить бути вирівняна");

static uint32_t crc32_bitwise(const void *buf, uint32_t n)
{
    const uint8_t *b = buf;
    uint32_t c = 0xffffffffu;
    for (uint32_t i = 0; i < n; i++) {
        c ^= b[i];
        for (int k = 0; k < 8; k++)
            c = (c >> 1) ^ (0xedb88320u & (uint32_t)-(int32_t)(c & 1));
    }
    return ~c;
}
