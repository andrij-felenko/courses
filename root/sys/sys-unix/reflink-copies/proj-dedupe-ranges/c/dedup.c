/* dedup.c — поблокова дедуплікація дерева через FIDEDUPERANGE. */
#define _GNU_SOURCE
#define _FILE_OFFSET_BITS 64

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>
#include <inttypes.h>
#include <errno.h>
#include <fcntl.h>
#include <unistd.h>
#include <ftw.h>
#include <sys/ioctl.h>
#include <sys/stat.h>
#include <linux/fs.h>
#include <linux/fiemap.h>

#define CHUNK (16u * 1024u * 1024u)   /* скільки просимо за один виклик */

static unsigned win = 128u * 1024u;   /* вікно хешування, кратне блокові ФС */

static uint64_t fmix64(uint64_t x)    /* фіналізатор MurmurHash3 */
{
    x ^= x >> 33; x *= 0xff51afd7ed558ccdULL;
    x ^= x >> 33; x *= 0xc4ceb9fe1a85ec53ULL;
    x ^= x >> 33;
    return x;
}

/* Хеш вікна. НЕ криптографічний і не мусить бути: останнє слово за ядром.
   Заразом кажемо, чи вікно суцільно нульове — такі не чіпаємо. */
static uint64_t blockhash(const unsigned char *p, size_t n, int *zero)
{
    uint64_t h = 0x9e3779b97f4a7c15ULL ^ (uint64_t)n, any = 0, w;
    for (size_t i = 0; i + 8 <= n; i += 8) {
        memcpy(&w, p + i, 8);
        any |= w;
        h = fmix64(h ^ w) + 0x9e3779b97f4a7c15ULL;
    }
    *zero = (any == 0);
    return fmix64(h);
}
