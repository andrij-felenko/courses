#ifndef SHA256_H
#define SHA256_H

/* Потоковий SHA-256. Саме потоковий: образ на кілька мегабайтів у SRAM
 * не влазить, тому хеш усього образу накопичується по секторах, поки
 * вони летять на Flash. */

#include <stddef.h>
#include <stdint.h>

#define SHA256_DIGEST_SIZE 32
#define SHA256_BLOCK_SIZE  64

typedef struct {
    uint32_t state[8];
    uint64_t bit_len;
    uint8_t  block[SHA256_BLOCK_SIZE];
    size_t   fill;
} sha256_ctx_t;

void sha256_init(sha256_ctx_t *ctx);
void sha256_update(sha256_ctx_t *ctx, const uint8_t *data, size_t len);
void sha256_final(sha256_ctx_t *ctx, uint8_t out[SHA256_DIGEST_SIZE]);

/* Разовий хеш одного сектора — саме ним звіряють чанк із таблицею. */
void sha256_once(const uint8_t *data, size_t len,
                 uint8_t out[SHA256_DIGEST_SIZE]);

#endif /* SHA256_H */
