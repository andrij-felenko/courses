#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

#define BLOCK_SIZE 64
#define STATE_WORDS 4

/* Контекст ітеративної хеш-функції Меркле — Дамґорда */
typedef struct {
    uint32_t state[STATE_WORDS];    /* Внутрішній стан (128 бітів) */
    uint64_t total_bits;            /* Загальна довжина обробленого повідомлення у бітах */
    uint8_t buffer[BLOCK_SIZE];     /* Буфер для накопичення поточного 64-байтового блоку */
    size_t buffer_len;              /* Кількість байтів у поточному буфері */
} md_ctx_t;

/* Циклічний зсув 32-бітового числа ліворуч на n бітів */
static uint32_t rotl32(uint32_t x, int n) {
    return (x << n) | (x >> (32 - n));
}

/* 
 * Основна ARX-функція стиснення f(state, block).
 * Обробляє один 64-байтовий блок і оновлює внутрішній стан.
 */
static void md_compress(uint32_t state[STATE_WORDS], const uint8_t block[BLOCK_SIZE]) {
    uint32_t w[16];

    /* Розпакування 64 байтів у 16 32-бітових слів (Little-Endian) */
    for (int i = 0; i < 16; i++) {
        w[i] = ((uint32_t)block[i * 4]) |
               ((uint32_t)block[i * 4 + 1] << 8) |
               ((uint32_t)block[i * 4 + 2] << 16) |
               ((uint32_t)block[i * 4 + 3] << 24);
    }

    uint32_t a = state[0];
    uint32_t b = state[1];
    uint32_t c = state[2];
    uint32_t d = state[3];

    /* 16 раундів перемішування ARX */
    for (int r = 0; r < 16; r++) {
        /* Нелінійна вибіркова функція Ch(b, c, d) */
        uint32_t f = (b & c) ^ (~b & d);
        uint32_t temp = a + f + w[r] + 0x5A827999U;
        a = d;
        d = c;
        c = b;
        b = b + rotl32(temp, 7);
    }

    /* Додавання початкового стану (Дамґордівська конкатенація Давіса — Майєра) */
    state[0] += a;
    state[1] += b;
    state[2] += c;
    state[3] += d;
}

/* Ініціалізація контексту хешування вектором IV */
void md_init(md_ctx_t *ctx) {
    ctx->state[0] = 0x67452301U;
    ctx->state[1] = 0xEFCDAB89U;
    ctx->state[2] = 0x98BADCFEU;
    ctx->state[3] = 0x10325476U;
    ctx->total_bits = 0;
    ctx->buffer_len = 0;
}

/* Послідовне оновлення хеша покомпонентно */
void md_update(md_ctx_t *ctx, const uint8_t *data, size_t len) {
    ctx->total_bits += ((uint64_t)len * 8);

    for (size_t i = 0; i < len; i++) {
        ctx->buffer[ctx->buffer_len++] = data[i];
        if (ctx->buffer_len == BLOCK_SIZE) {
            md_compress(ctx->state, ctx->buffer);
            ctx->buffer_len = 0;
        }
    }
}

/* Завершення обчислення хеша: підкладка, додавання довжини та фінальне стиснення */
void md_final(md_ctx_t *ctx, uint8_t digest[16]) {
    /* Байт 0x80 позначає початок підкладки */
    ctx->buffer[ctx->buffer_len++] = 0x80;

    /* Якщо в блоці не вистачає місця для 8 байтів довжини */
    if (ctx->buffer_len > 56) {
        while (ctx->buffer_len < BLOCK_SIZE) {
            ctx->buffer[ctx->buffer_len++] = 0x00;
        }
        md_compress(ctx->state, ctx->buffer);
        ctx->buffer_len = 0;
    }

    /* Доповнення нулями до 56 байтів */
    while (ctx->buffer_len < 56) {
        ctx->buffer[ctx->buffer_len++] = 0x00;
    }

    /* Запис 64-бітової довжини повідомлення у бітах (Little-Endian) */
    uint64_t bits = ctx->total_bits;
    for (int i = 0; i < 8; i++) {
        ctx->buffer[56 + i] = (uint8_t)(bits >> (i * 8));
    }

    md_compress(ctx->state, ctx->buffer);

    /* Формування фінального 16-байтового відбитка */
    for (int i = 0; i < 4; i++) {
        digest[i * 4]     = (uint8_t)(ctx->state[i]);
        digest[i * 4 + 1] = (uint8_t)(ctx->state[i] >> 8);
        digest[i * 4 + 2] = (uint8_t)(ctx->state[i] >> 16);
        digest[i * 4 + 3] = (uint8_t)(ctx->state[i] >> 24);
    }
}

/* Реалізація захищеного підпису HMAC */
void hmac_md(const uint8_t *key, size_t key_len, const uint8_t *msg, size_t msg_len, uint8_t out[16]) {
    uint8_t k_padded[BLOCK_SIZE] = {0};

    if (key_len > BLOCK_SIZE) {
        md_ctx_t k_ctx;
        md_init(&k_ctx);
        md_update(&k_ctx, key, key_len);
        md_final(&k_ctx, k_padded);
    } else {
        memcpy(k_padded, key, key_len);
    }

    uint8_t i_key[BLOCK_SIZE];
    uint8_t o_key[BLOCK_SIZE];

    for (int i = 0; i < BLOCK_SIZE; i++) {
        i_key[i] = k_padded[i] ^ 0x36;
        o_key[i] = k_padded[i] ^ 0x5C;
    }

    /* Внутрішній крок: H((K ⊕ ipad) || M) */
    uint8_t inner_digest[16];
    md_ctx_t ctx;
    md_init(&ctx);
    md_update(&ctx, i_key, BLOCK_SIZE);
    md_update(&ctx, msg, msg_len);
    md_final(&ctx, inner_digest);

    /* Зовнішній крок: H((K ⊕ opad) || inner_digest) */
    md_init(&ctx);
    md_update(&ctx, o_key, BLOCK_SIZE);
    md_update(&ctx, inner_digest, 16);
    md_final(&ctx, out);
}

int main(void) {
    const char *message = "action=transfer&amount=100";
    md_ctx_t ctx;
    uint8_t digest[16];

    md_init(&ctx);
    md_update(&ctx, (const uint8_t*)message, strlen(message));
    md_final(&ctx, digest);

    printf("Хеш вхідного повідомлення: ");
    for (int i = 0; i < 16; i++) printf("%02x", digest[i]);
    printf("\n");

    uint8_t hmac_out[16];
    const char *key = "secret_key";
    hmac_md((const uint8_t*)key, strlen(key), (const uint8_t*)message, strlen(message), hmac_out);
    printf("HMAC захищений підпис:     ");
    for (int i = 0; i < 16; i++) printf("%02x", hmac_out[i]);
    printf("\n");

    return 0;
}
