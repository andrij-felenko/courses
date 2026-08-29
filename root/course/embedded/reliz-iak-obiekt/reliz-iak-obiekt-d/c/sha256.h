#ifndef SHA256_H
#define SHA256_H

#include <stdint.h>
#include <stddef.h>

/* Потоковий SHA-256: завантажувач ніколи не тримає весь образ у пам'яті —
   він згодовує його шматками по мірі читання з Flash. */
typedef struct {
    uint32_t state[8];
    uint64_t total_bits;
    uint8_t  block[64];
    size_t   used;
} sha256_t;

void sha256_init(sha256_t *ctx);
void sha256_update(sha256_t *ctx, const void *data, size_t len);
void sha256_final(sha256_t *ctx, uint8_t out[32]);

#endif /* SHA256_H */
