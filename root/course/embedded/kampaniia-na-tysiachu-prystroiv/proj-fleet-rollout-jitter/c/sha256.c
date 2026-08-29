#include "sha256.h"

#include <string.h>

#define ROTR(x, n) (((x) >> (n)) | ((x) << (32 - (n))))

static const uint32_t K[64] = {
    0x428a2f98u, 0x71374491u, 0xb5c0fbcfu, 0xe9b5dba5u,
    0x3956c25bu, 0x59f111f1u, 0x923f82a4u, 0xab1c5ed5u,
    0xd807aa98u, 0x12835b01u, 0x243185beu, 0x550c7dc3u,
    0x72be5d74u, 0x80deb1feu, 0x9bdc06a7u, 0xc19bf174u,
    0xe49b69c1u, 0xefbe4786u, 0x0fc19dc6u, 0x240ca1ccu,
    0x2de92c6fu, 0x4a7484aau, 0x5cb0a9dcu, 0x76f988dau,
    0x983e5152u, 0xa831c66du, 0xb00327c8u, 0xbf597fc7u,
    0xc6e00bf3u, 0xd5a79147u, 0x06ca6351u, 0x14292967u,
    0x27b70a85u, 0x2e1b2138u, 0x4d2c6dfcu, 0x53380d13u,
    0x650a7354u, 0x766a0abbu, 0x81c2c92eu, 0x92722c85u,
    0xa2bfe8a1u, 0xa81a664bu, 0xc24b8b70u, 0xc76c51a3u,
    0xd192e819u, 0xd6990624u, 0xf40e3585u, 0x106aa070u,
    0x19a4c116u, 0x1e376c08u, 0x2748774cu, 0x34b0bcb5u,
    0x391c0cb3u, 0x4ed8aa4au, 0x5b9cca4fu, 0x682e6ff3u,
    0x748f82eeu, 0x78a5636fu, 0x84c87814u, 0x8cc70208u,
    0x90befffau, 0xa4506cebu, 0xbef9a3f7u, 0xc67178f2u
};

static void sha256_block(sha256_ctx_t *ctx, const uint8_t block[64])
{
    uint32_t w[64];

    for (unsigned i = 0; i < 16; ++i) {
        w[i] = ((uint32_t)block[4u * i + 0] << 24) |
               ((uint32_t)block[4u * i + 1] << 16) |
               ((uint32_t)block[4u * i + 2] << 8)  |
               ((uint32_t)block[4u * i + 3]);
    }
    for (unsigned i = 16; i < 64; ++i) {
        const uint32_t s0 = ROTR(w[i - 15], 7) ^ ROTR(w[i - 15], 18) ^ (w[i - 15] >> 3);
        const uint32_t s1 = ROTR(w[i - 2], 17) ^ ROTR(w[i - 2], 19) ^ (w[i - 2] >> 10);
        w[i] = w[i - 16] + s0 + w[i - 7] + s1;
    }

    uint32_t a = ctx->h[0], b = ctx->h[1], c = ctx->h[2], d = ctx->h[3];
    uint32_t e = ctx->h[4], f = ctx->h[5], g = ctx->h[6], h = ctx->h[7];

    for (unsigned i = 0; i < 64; ++i) {
        const uint32_t s1 = ROTR(e, 6) ^ ROTR(e, 11) ^ ROTR(e, 25);
        const uint32_t ch = (e & f) ^ (~e & g);
        const uint32_t t1 = h + s1 + ch + K[i] + w[i];
        const uint32_t s0 = ROTR(a, 2) ^ ROTR(a, 13) ^ ROTR(a, 22);
        const uint32_t maj = (a & b) ^ (a & c) ^ (b & c);
        const uint32_t t2 = s0 + maj;

        h = g; g = f; f = e;
        e = d + t1;
        d = c; c = b; b = a;
        a = t1 + t2;
    }

    ctx->h[0] += a; ctx->h[1] += b; ctx->h[2] += c; ctx->h[3] += d;
    ctx->h[4] += e; ctx->h[5] += f; ctx->h[6] += g; ctx->h[7] += h;
}

void sha256_init(sha256_ctx_t *ctx)
{
    ctx->h[0] = 0x6a09e667u; ctx->h[1] = 0xbb67ae85u;
    ctx->h[2] = 0x3c6ef372u; ctx->h[3] = 0xa54ff53au;
    ctx->h[4] = 0x510e527fu; ctx->h[5] = 0x9b05688cu;
    ctx->h[6] = 0x1f83d9abu; ctx->h[7] = 0x5be0cd19u;
    ctx->bits = 0;
    ctx->buf_len = 0;
}

void sha256_update(sha256_ctx_t *ctx, const uint8_t *data, size_t len)
{
    if (data == NULL) {
        return;
    }
    ctx->bits += (uint64_t)len * 8u;

    /* Добираємо хвіст попереднього виклику до повного блоку. */
    if (ctx->buf_len > 0) {
        const size_t need = 64u - ctx->buf_len;
        const size_t take = (len < need) ? len : need;
        memcpy(ctx->buf + ctx->buf_len, data, take);
        ctx->buf_len += take;
        data += take;
        len  -= take;
        if (ctx->buf_len == 64u) {
            sha256_block(ctx, ctx->buf);
            ctx->buf_len = 0;
        }
    }

    while (len >= 64u) {
        sha256_block(ctx, data);
        data += 64u;
        len  -= 64u;
    }

    if (len > 0) {
        memcpy(ctx->buf, data, len);
        ctx->buf_len = len;
    }
}

void sha256_final(sha256_ctx_t *ctx, uint8_t out[SHA256_DIGEST_LEN])
{
    const uint64_t bits = ctx->bits;

    /* Доповнення: 0x80, нулі, 64-бітна довжина у бітах старшим байтом уперед. */
    ctx->buf[ctx->buf_len++] = 0x80u;
    if (ctx->buf_len > 56u) {
        memset(ctx->buf + ctx->buf_len, 0, 64u - ctx->buf_len);
        sha256_block(ctx, ctx->buf);
        ctx->buf_len = 0;
    }
    memset(ctx->buf + ctx->buf_len, 0, 56u - ctx->buf_len);
    for (unsigned i = 0; i < 8; ++i) {
        ctx->buf[56u + i] = (uint8_t)(bits >> (56u - 8u * i));
    }
    sha256_block(ctx, ctx->buf);

    for (unsigned i = 0; i < 8; ++i) {
        out[4u * i + 0] = (uint8_t)(ctx->h[i] >> 24);
        out[4u * i + 1] = (uint8_t)(ctx->h[i] >> 16);
        out[4u * i + 2] = (uint8_t)(ctx->h[i] >> 8);
        out[4u * i + 3] = (uint8_t)(ctx->h[i]);
    }
    memset(ctx, 0, sizeof(*ctx));
}

void sha256_pair(const uint8_t *a, size_t a_len,
                 const uint8_t *b, size_t b_len,
                 uint8_t out[SHA256_DIGEST_LEN])
{
    sha256_ctx_t ctx;
    sha256_init(&ctx);
    sha256_update(&ctx, a, a_len);
    sha256_update(&ctx, b, b_len);
    sha256_final(&ctx, out);
}
