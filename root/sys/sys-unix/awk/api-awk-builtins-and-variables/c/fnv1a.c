#include "fnv1a.h"

#include <inttypes.h>
#include <stdio.h>

#define FNV_OFFSET_BASIS_64 UINT64_C(14695981039346656037)
#define FNV_PRIME_64        UINT64_C(1099511628211)

uint64_t fnv1a_64(const void *data, size_t len)
{
    const uint8_t *bytes = (const uint8_t *) data;
    uint64_t hash = FNV_OFFSET_BASIS_64;
    size_t i;

    if (bytes == NULL)
        len = 0;

    for (i = 0; i < len; i++) {
        hash ^= bytes[i];
        /* Беззнакове множення: переповнення визначене стандартом і є саме
           тим, чого хеш і хоче — обрізанням за модулем 2^64. */
        hash *= FNV_PRIME_64;
    }
    return hash;
}

int fnv1a_64_hex(uint64_t hash, char *buf, size_t size)
{
    int written;

    if (buf == NULL || size < FNV1A_HEX_SIZE)
        return -1;

    written = snprintf(buf, size, "0x%016" PRIx64, hash);
    if (written < 0 || (size_t) written >= size)
        return -1;
    return written;
}
