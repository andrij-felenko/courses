#include "sha256.h"

#include <string.h>

/* Реалізація за FIPS 180-4. Тримаємо її у проєкті свідомо: криптобібліотека
   для Ed25519 (Monocypher) SHA-256 не має, а тягнути другу бібліотеку заради
   однієї геш-функції в завантажувач на кілька кілобайтів RAM — надмір. */

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

static uint32_t rotr(uint32_t x, unsigned n)
{
    return (x >> n) | (x << (32u - n));
}

#define CH(x, y, z)    (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z)   (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define BSIG0(x)       (rotr((x), 2)  ^ rotr((x), 13) ^ rotr((x), 22))
#define BSIG1(x)       (rotr((x), 6)  ^ rotr((x), 11) ^ rotr((x), 25))
#define SSIG0(x)       (rotr((x), 7)  ^ rotr((x), 18) ^ ((x) >> 3))
#define SSIG1(x)       (rotr((x), 17) ^ rotr((x), 19) ^ ((x) >> 10))

/* Стиснення одного 64-байтного блоку. w[64] — це 256 байтів стека; для
   завантажувача, якому виділено 2 КБ, це прийнятно, але знати треба. */
static void sha256_compress(sha256_t *ctx, const uint8_t block[64])
{
    uint32_t w[64];
    uint32_t a, b, c, d, e, f, g, h;
    unsigned i;

    for (i = 0; i < 16; i++) {
        w[i] = ((uint32_t)block[4u * i + 0u] << 24) |
               ((uint32_t)block[4u * i + 1u] << 16) |
               ((uint32_t)block[4u * i + 2u] << 8)  |
               ((uint32_t)block[4u * i + 3u]);
    }
    for (i = 16; i < 64; i++) {
        w[i] = SSIG1(w[i - 2]) + w[i - 7] + SSIG0(w[i - 15]) + w[i - 16];
    }

    a = ctx->state[0]; b = ctx->state[1]; c = ctx->state[2]; d = ctx->state[3];
    e = ctx->state[4]; f = ctx->state[5]; g = ctx->state[6]; h = ctx->state[7];

    for (i = 0; i < 64; i++) {
        const uint32_t t1 = h + BSIG1(e) + CH(e, f, g) + K[i] + w[i];
        const uint32_t t2 = BSIG0(a) + MAJ(a, b, c);
        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }

    ctx->state[0] += a; ctx->state[1] += b; ctx->state[2] += c; ctx->state[3] += d;
    ctx->state[4] += e; ctx->state[5] += f; ctx->state[6] += g; ctx->state[7] += h;
}

void sha256_init(sha256_t *ctx)
{
    ctx->state[0] = 0x6a09e667u; ctx->state[1] = 0xbb67ae85u;
    ctx->state[2] = 0x3c6ef372u; ctx->state[3] = 0xa54ff53au;
    ctx->state[4] = 0x510e527fu; ctx->state[5] = 0x9b05688cu;
    ctx->state[6] = 0x1f83d9abu; ctx->state[7] = 0x5be0cd19u;
    ctx->total_bits = 0u;
    ctx->used = 0u;
    memset(ctx->block, 0, sizeof ctx->block);
}

void sha256_update(sha256_t *ctx, const void *data, size_t len)
{
    const uint8_t *p = (const uint8_t *)data;

    ctx->total_bits += (uint64_t)len * 8u;

    /* Спершу добиваємо недобраний хвіст попереднього виклику. */
    if (ctx->used > 0u) {
        size_t need = 64u - ctx->used;
        if (need > len) {
            need = len;
        }
        memcpy(ctx->block + ctx->used, p, need);
        ctx->used += need;
        p += need;
        len -= need;
        if (ctx->used == 64u) {
            sha256_compress(ctx, ctx->block);
            ctx->used = 0u;
        }
    }

    /* Цілі блоки жують просто з вхідного буфера, без копіювання. */
    while (len >= 64u) {
        sha256_compress(ctx, p);
        p += 64u;
        len -= 64u;
    }

    if (len > 0u) {
        memcpy(ctx->block, p, len);
        ctx->used = len;
    }
}

void sha256_final(sha256_t *ctx, uint8_t out[32])
{
    const uint64_t bits = ctx->total_bits;
    unsigned i;

    /* Доповнення: байт 0x80, нулі до зсуву 56, далі 64-бітна довжина в бітах
       старшим байтом уперед. Якщо місця під довжину не лишилось — ще блок. */
    ctx->block[ctx->used++] = 0x80u;
    if (ctx->used > 56u) {
        memset(ctx->block + ctx->used, 0, 64u - ctx->used);
        sha256_compress(ctx, ctx->block);
        ctx->used = 0u;
    }
    memset(ctx->block + ctx->used, 0, 56u - ctx->used);
    for (i = 0; i < 8u; i++) {
        ctx->block[56u + i] = (uint8_t)(bits >> (56u - 8u * i));
    }
    sha256_compress(ctx, ctx->block);

    for (i = 0; i < 8u; i++) {
        out[4u * i + 0u] = (uint8_t)(ctx->state[i] >> 24);
        out[4u * i + 1u] = (uint8_t)(ctx->state[i] >> 16);
        out[4u * i + 2u] = (uint8_t)(ctx->state[i] >> 8);
        out[4u * i + 3u] = (uint8_t)(ctx->state[i]);
    }

    /* Стан затираємо: у завантажувачі буфери переживають повернення з функції,
       а лишати чужі байти в RAM перед стрибком у застосунок — погана звичка. */
    memset(ctx, 0, sizeof *ctx);
}
