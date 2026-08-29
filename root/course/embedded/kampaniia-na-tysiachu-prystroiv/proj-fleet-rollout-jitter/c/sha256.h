/* SHA-256 — рахує номер когорти й підписний дайджест образу.
 * На кристалах із блоком HASH цей модуль замінює драйвер прискорювача;
 * інтерфейс лишається той самий. */
#ifndef SHA256_H
#define SHA256_H

#include <stddef.h>
#include <stdint.h>

#define SHA256_DIGEST_LEN 32u

typedef struct {
    uint32_t h[8];
    uint64_t bits;
    uint8_t  buf[64];
    size_t   buf_len;
} sha256_ctx_t;

void sha256_init(sha256_ctx_t *ctx);
void sha256_update(sha256_ctx_t *ctx, const uint8_t *data, size_t len);
void sha256_final(sha256_ctx_t *ctx, uint8_t out[SHA256_DIGEST_LEN]);

/* Разовий виклик над двома частинами — саме так рахується hw_id || campaign_salt. */
void sha256_pair(const uint8_t *a, size_t a_len,
                 const uint8_t *b, size_t b_len,
                 uint8_t out[SHA256_DIGEST_LEN]);

#endif /* SHA256_H */
