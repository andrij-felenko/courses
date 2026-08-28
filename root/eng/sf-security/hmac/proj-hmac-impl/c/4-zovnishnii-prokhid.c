#include <stdint.h>
#include <stddef.h>
#include <string.h>

#define SHA256_BLOCK_SIZE 64
#define SHA256_DIGEST_SIZE 32

/* Базовий контекст SHA-256 */
typedef struct {
    uint32_t state[8];
    uint64_t count;
    uint8_t buffer[SHA256_BLOCK_SIZE];
} sha256_ctx_t;

/* Допоміжні функції бітових операцій SHA-256 */
static inline uint32_t rotr(uint32_t x, uint32_t n) {
    return (x >> n) | (x << (32 - n));
}
#define CH(x, y, z)  (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z) (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define EP0(x)       (rotr(x, 2) ^ rotr(x, 13) ^ rotr(x, 22))
#define EP1(x)       (rotr(x, 6) ^ rotr(x, 11) ^ rotr(x, 25))
#define SIG0(x)      (rotr(x, 7) ^ rotr(x, 18) ^ ((x) >> 3))
#define SIG1(x)      (rotr(x, 17) ^ rotr(x, 19) ^ ((x) >> 10))

static const uint32_t K256[64] = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2
};

static void sha256_transform(sha256_ctx_t *ctx, const uint8_t data[64]) {
    uint32_t a, b, c, d, e, f, g, h, w[64];
    for (int i = 0; i < 16; i++) {
        w[i] = ((uint32_t)data[i * 4] << 24) | ((uint32_t)data[i * 4 + 1] << 16) |
               ((uint32_t)data[i * 4 + 2] << 8) | ((uint32_t)data[i * 4 + 3]);
    }
    for (int i = 16; i < 64; i++) {
        w[i] = SIG1(w[i - 2]) + w[i - 7] + SIG0(w[i - 15]) + w[i - 16];
    }
    a = ctx->state[0]; b = ctx->state[1]; c = ctx->state[2]; d = ctx->state[3];
    e = ctx->state[4]; f = ctx->state[5]; g = ctx->state[6]; h = ctx->state[7];

    for (int i = 0; i < 64; i++) {
        uint32_t t1 = h + EP1(e) + CH(e, f, g) + K256[i] + w[i];
        uint32_t t2 = EP0(a) + MAJ(a, b, c);
        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }
    ctx->state[0] += a; ctx->state[1] += b; ctx->state[2] += c; ctx->state[3] += d;
    ctx->state[4] += e; ctx->state[5] += f; ctx->state[6] += g; ctx->state[7] += h;
}

void sha256_init(sha256_ctx_t *ctx) {
    ctx->state[0] = 0x6a09e667; ctx->state[1] = 0xbb67ae85;
    ctx->state[2] = 0x3c6ef372; ctx->state[3] = 0xa54ff53a;
    ctx->state[4] = 0x510e527f; ctx->state[5] = 0x9b05688c;
    ctx->state[6] = 0x1f83d9ab; ctx->state[7] = 0x5be0cd19;
    ctx->count = 0;
}

void sha256_update(sha256_ctx_t *ctx, const uint8_t *data, size_t len) {
    size_t buf_idx = (size_t)(ctx->count % SHA256_BLOCK_SIZE);
    ctx->count += len;
    while (len > 0) {
        size_t copy_len = SHA256_BLOCK_SIZE - buf_idx;
        if (len < copy_len) copy_len = len;
        memcpy(&ctx->buffer[buf_idx], data, copy_len);
        data += copy_len;
        len -= copy_len;
        buf_idx = (buf_idx + copy_len) % SHA256_BLOCK_SIZE;
        if (buf_idx == 0) {
            sha256_transform(ctx, ctx->buffer);
        }
    }
}

void sha256_final(sha256_ctx_t *ctx, uint8_t digest[SHA256_DIGEST_SIZE]) {
    uint8_t pad[64] = {0x80};
    uint64_t bitlen = ctx->count * 8;
    uint8_t len_bytes[8];
    for (int i = 0; i < 8; i++) {
        len_bytes[7 - i] = (uint8_t)(bitlen >> (i * 8));
    }
    size_t pad_len = (ctx->count % 64 < 56) ? (56 - (ctx->count % 64)) : (120 - (ctx->count % 64));
    sha256_update(ctx, pad, pad_len);
    sha256_update(ctx, len_bytes, 8);
    for (int i = 0; i < 8; i++) {
        digest[i * 4]     = (uint8_t)(ctx->state[i] >> 24);
        digest[i * 4 + 1] = (uint8_t)(ctx->state[i] >> 16);
        digest[i * 4 + 2] = (uint8_t)(ctx->state[i] >> 8);
        digest[i * 4 + 3] = (uint8_t)(ctx->state[i]);
    }
}

/* Структура контексту HMAC-SHA256 */
typedef struct {
    sha256_ctx_t inner_ctx;
    sha256_ctx_t outer_ctx;
} hmac_sha256_ctx_t;

void hmac_sha256_init(hmac_sha256_ctx_t *ctx, const uint8_t *key, size_t key_len) {
    uint8_t k_prime[SHA256_BLOCK_SIZE] = {0};
    uint8_t k_ipad[SHA256_BLOCK_SIZE];
    uint8_t k_opad[SHA256_BLOCK_SIZE];

    /* 1. Нормалізація ключа */
    if (key_len > SHA256_BLOCK_SIZE) {
        sha256_ctx_t k_ctx;
        sha256_init(&k_ctx);
        sha256_update(&k_ctx, key, key_len);
        sha256_final(&k_ctx, k_prime);
    } else {
        memcpy(k_prime, key, key_len);
    }

    /* 2. Побітове накладання масок ipad (0x36) та opad (0x5C) */
    for (size_t i = 0; i < SHA256_BLOCK_SIZE; i++) {
        k_ipad[i] = k_prime[i] ^ 0x36;
        k_opad[i] = k_prime[i] ^ 0x5C;
    }

    /* 3. Ініціалізація внутрішнього та зовнішнього каскадів */
    sha256_init(&ctx->inner_ctx);
    sha256_update(&ctx->inner_ctx, k_ipad, SHA256_BLOCK_SIZE);

    sha256_init(&ctx->outer_ctx);
    sha256_update(&ctx->outer_ctx, k_opad, SHA256_BLOCK_SIZE);

    /* Безпечне очищення тимчасових буферів ключа у стеку */
    memset(k_prime, 0, sizeof(k_prime));
    memset(k_ipad, 0, sizeof(k_ipad));
    memset(k_opad, 0, sizeof(k_opad));
}

void hmac_sha256_update(hmac_sha256_ctx_t *ctx, const uint8_t *data, size_t len) {
    sha256_update(&ctx->inner_ctx, data, len);
}

void hmac_sha256_final(hmac_sha256_ctx_t *ctx, uint8_t mac[SHA256_DIGEST_SIZE]) {
    uint8_t inner_digest[SHA256_DIGEST_SIZE];
    sha256_final(&ctx->inner_ctx, inner_digest);
    sha256_update(&ctx->outer_ctx, inner_digest, SHA256_DIGEST_SIZE);
    sha256_final(&ctx->outer_ctx, mac);
    memset(inner_digest, 0, sizeof(inner_digest));
}

/* Одноразовий виклик HMAC-SHA256 */
void hmac_sha256(const uint8_t *key, size_t key_len,
                 const uint8_t *msg, size_t msg_len,
                 uint8_t out[SHA256_DIGEST_SIZE]) {
    hmac_sha256_ctx_t ctx;
    hmac_sha256_init(&ctx, key, key_len);
    hmac_sha256_update(&ctx, msg, msg_len);
    hmac_sha256_final(&ctx, out);
}
