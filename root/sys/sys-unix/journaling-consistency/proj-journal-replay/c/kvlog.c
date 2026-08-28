/* kvlog.c — сховище «ключ→значення» з власним журналом.
 * Збірка:  cc -O2 -Wall -Wextra -o kvlog kvlog.c
 */
#define _POSIX_C_SOURCE 200809L
#include <errno.h>
#include <fcntl.h>
#include <libgen.h>
#include <stdint.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>

#define MAGIC     0x314C564Bu
#define SEAL      0x214C4145u
#define HDR       16
#define TRL       8
#define MAX_BODY  (1u << 20)
#define OP_PUT    1
#define OP_DEL    2

static void put_u32(uint8_t *p, uint32_t v) {
    p[0] = (uint8_t)v;         p[1] = (uint8_t)(v >> 8);
    p[2] = (uint8_t)(v >> 16); p[3] = (uint8_t)(v >> 24);
}
static uint32_t get_u32(const uint8_t *p) {
    return (uint32_t)p[0]        | ((uint32_t)p[1] << 8)
         | ((uint32_t)p[2] << 16) | ((uint32_t)p[3] << 24);
}
static void put_u64(uint8_t *p, uint64_t v) {
    put_u32(p, (uint32_t)v);  put_u32(p + 4, (uint32_t)(v >> 32));
}
static uint64_t get_u64(const uint8_t *p) {
    return (uint64_t)get_u32(p) | ((uint64_t)get_u32(p + 4) << 32);
}

/* CRC-32 (той самий поліном, що в zip, gzip і ext4) — побітово, без таблиці:
   для нашого обсягу швидкості вистачає, а читати коротше. */
static uint32_t crc32(const uint8_t *buf, size_t n) {
    uint32_t c = 0xFFFFFFFFu;
    for (size_t i = 0; i < n; i++) {
        c ^= buf[i];
        for (int k = 0; k < 8; k++)
            c = (c >> 1) ^ (0xEDB88320u & (uint32_t)(-(int32_t)(c & 1)));
    }
    return c ^ 0xFFFFFFFFu;
}
