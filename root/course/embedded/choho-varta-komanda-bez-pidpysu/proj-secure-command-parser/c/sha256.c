#include "sha256.h"

#include <string.h>

static const uint32_t K[64] = {
    0x428a2f98U, 0x71374491U, 0xb5c0fbcfU, 0xe9b5dba5U,
    0x3956c25bU, 0x59f111f1U, 0x923f82a4U, 0xab1c5ed5U,
    0xd807aa98U, 0x12835b01U, 0x243185beU, 0x550c7dc3U,
    0x72be5d74U, 0x80deb1feU, 0x9bdc06a7U, 0xc19bf174U,
    0xe49b69c1U, 0xefbe4786U, 0x0fc19dc6U, 0x240ca1ccU,
    0x2de92c6fU, 0x4a7484aaU, 0x5cb0a9dcU, 0x76f988daU,
    0x983e5152U, 0xa831c66dU, 0xb00327c8U, 0xbf597fc7U,
    0xc6e00bf3U, 0xd5a79147U, 0x06ca6351U, 0x14292967U,
    0x27b70a85U, 0x2e1b2138U, 0x4d2c6dfcU, 0x53380d13U,
    0x650a7354U, 0x766a0abbU, 0x81c2c92eU, 0x92722c85U,
    0xa2bfe8a1U, 0xa81a664bU, 0xc24b8b70U, 0xc76c51a3U,
    0xd192e819U, 0xd6990624U, 0xf40e3585U, 0x106aa070U,
    0x19a4c116U, 0x1e376c08U, 0x2748774cU, 0x34b0bcb5U,
    0x391c0cb3U, 0x4ed8aa4aU, 0x5b9cca4fU, 0x682e6ff3U,
    0x748f82eeU, 0x78a5636fU, 0x84c87814U, 0x8cc70208U,
    0x90befffaU, 0xa4506cebU, 0xbef9a3f7U, 0xc67178f2U
};

static uint32_t rotr(uint32_t x, unsigned n)
{
    return (x >> n) | (x << (32U - n));
}

/* Читання й запис 32-бітних слів у мережевому порядку байтів — побайтово,
 * бо блок може лежати за невирівняною адресою DMA-буфера. */
static uint32_t load_be32(const uint8_t *p)
{
    return ((uint32_t)p[0] << 24) | ((uint32_t)p[1] << 16)
         | ((uint32_t)p[2] << 8)  |  (uint32_t)p[3];
}

static void store_be32(uint8_t *p, uint32_t v)
{
    p[0] = (uint8_t)(v >> 24);
    p[1] = (uint8_t)(v >> 16);
    p[2] = (uint8_t)(v >> 8);
    p[3] = (uint8_t)v;
}

#define CH(x, y, z)   (((x) & (y)) ^ (~(x) & (z)))
#define MAJ(x, y, z)  (((x) & (y)) ^ ((x) & (z)) ^ ((y) & (z)))
#define BSIG0(x)      (rotr((x), 2)  ^ rotr((x), 13) ^ rotr((x), 22))
#define BSIG1(x)      (rotr((x), 6)  ^ rotr((x), 11) ^ rotr((x), 25))
#define SSIG0(x)      (rotr((x), 7)  ^ rotr((x), 18) ^ ((x) >> 3))
#define SSIG1(x)      (rotr((x), 17) ^ rotr((x), 19) ^ ((x) >> 10))

/*
 * Стиск одного 64-байтного блоку.
 *
 * Розклад повідомлення тримаємо в кільці з шістнадцяти слів, а не в масиві
 * на 64: це 64 байти стеку замість 256. На Cortex-M0 з 8 КБ RAM така різниця
 * вирішує, влізе модуль у стек мережевого завдання чи ні.
 */
static void sha256_compress(uint32_t state[8], const uint8_t block[SHA256_BLOCK_SIZE])
{
    uint32_t w[16];
    uint32_t a = state[0], b = state[1], c = state[2], d = state[3];
    uint32_t e = state[4], f = state[5], g = state[6], h = state[7];

    for (unsigned i = 0; i < 64; ++i) {
        uint32_t wi;
        if (i < 16) {
            wi = load_be32(block + 4U * i);
            w[i] = wi;
        } else {
            /* W[i] = SSIG1(W[i-2]) + W[i-7] + SSIG0(W[i-15]) + W[i-16] */
            wi = w[i & 15U]
               + SSIG0(w[(i + 1U) & 15U])
               + w[(i + 9U) & 15U]
               + SSIG1(w[(i + 14U) & 15U]);
            w[i & 15U] = wi;
        }

        uint32_t t1 = h + BSIG1(e) + CH(e, f, g) + K[i] + wi;
        uint32_t t2 = BSIG0(a) + MAJ(a, b, c);

        h = g; g = f; f = e; e = d + t1;
        d = c; c = b; b = a; a = t1 + t2;
    }

    state[0] += a; state[1] += b; state[2] += c; state[3] += d;
    state[4] += e; state[5] += f; state[6] += g; state[7] += h;

    crypto_wipe(w, sizeof w);
}

void sha256_init(Sha256Ctx *ctx)
{
    ctx->h[0] = 0x6a09e667U; ctx->h[1] = 0xbb67ae85U;
    ctx->h[2] = 0x3c6ef372U; ctx->h[3] = 0xa54ff53aU;
    ctx->h[4] = 0x510e527fU; ctx->h[5] = 0x9b05688cU;
    ctx->h[6] = 0x1f83d9abU; ctx->h[7] = 0x5be0cd19U;
    ctx->total_len = 0;
    ctx->buf_len = 0;
    memset(ctx->buf, 0, sizeof ctx->buf);
}

void sha256_update(Sha256Ctx *ctx, const uint8_t *data, size_t len)
{
    ctx->total_len += (uint64_t)len;

    /* Добираємо хвіст попереднього виклику до повного блоку. */
    if (ctx->buf_len != 0) {
        size_t need = SHA256_BLOCK_SIZE - ctx->buf_len;
        size_t take = (len < need) ? len : need;
        memcpy(ctx->buf + ctx->buf_len, data, take);
        ctx->buf_len += take;
        data += take;
        len  -= take;
        if (ctx->buf_len < SHA256_BLOCK_SIZE) {
            return;             /* блок ще не повний — чекаємо наступних даних */
        }
        sha256_compress(ctx->h, ctx->buf);
        ctx->buf_len = 0;
    }

    /* Повні блоки беремо просто з вхідного буфера, без проміжного копіювання. */
    while (len >= SHA256_BLOCK_SIZE) {
        sha256_compress(ctx->h, data);
        data += SHA256_BLOCK_SIZE;
        len  -= SHA256_BLOCK_SIZE;
    }

    if (len != 0) {
        memcpy(ctx->buf, data, len);
        ctx->buf_len = len;
    }
}

void sha256_final(Sha256Ctx *ctx, uint8_t out[SHA256_DIGEST_SIZE])
{
    uint64_t bit_len = ctx->total_len * 8U;

    /* Доповнення: одиничний біт, нулі, і 64-бітна довжина в бітах у кінці. */
    ctx->buf[ctx->buf_len++] = 0x80U;
    if (ctx->buf_len > SHA256_BLOCK_SIZE - 8U) {
        memset(ctx->buf + ctx->buf_len, 0, SHA256_BLOCK_SIZE - ctx->buf_len);
        sha256_compress(ctx->h, ctx->buf);
        ctx->buf_len = 0;
    }
    memset(ctx->buf + ctx->buf_len, 0, (SHA256_BLOCK_SIZE - 8U) - ctx->buf_len);
    store_be32(ctx->buf + SHA256_BLOCK_SIZE - 8U, (uint32_t)(bit_len >> 32));
    store_be32(ctx->buf + SHA256_BLOCK_SIZE - 4U, (uint32_t)bit_len);
    sha256_compress(ctx->h, ctx->buf);

    for (unsigned i = 0; i < 8U; ++i) {
        store_be32(out + 4U * i, ctx->h[i]);
    }

    crypto_wipe(ctx, sizeof *ctx);
}

void sha256(const uint8_t *data, size_t len, uint8_t out[SHA256_DIGEST_SIZE])
{
    Sha256Ctx ctx;
    sha256_init(&ctx);
    sha256_update(&ctx, data, len);
    sha256_final(&ctx, out);
}

void crypto_wipe(void *p, size_t len)
{
    volatile uint8_t *q = (volatile uint8_t *)p;
    while (len-- != 0) {
        *q++ = 0;
    }
}
