#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <stdint.h>

/* Структура безпекового контексту OSCORE відповідно до RFC 8613 */
typedef struct {
    uint8_t master_secret[16];
    uint8_t master_salt[8];
    uint8_t sender_id[4];
    uint8_t recipient_id[4];
    uint8_t sender_key[16];
    uint8_t recipient_key[16];
    uint8_t common_iv[13];
    uint64_t sequence_number;
} oscore_context_t;

/* Спрощена імітація функції HKDF-Extract/Expand для виведення сесійних ключів */
void oscore_derive_key(const uint8_t *secret, const uint8_t *salt, const char *label, uint8_t *out, size_t out_len) {
    /* Просте XOR-поєднання параметрів для навчальної демонстрації */
    for (size_t i = 0; i < out_len; i++) {
        out[i] = secret[i % 16] ^ salt[i % 8] ^ (uint8_t)label[i % strlen(label)];
    }
}

/* Ініціалізація контексту OSCORE */
int oscore_context_init(oscore_context_t *ctx) {
    if (!ctx) return -1;

    /* Встановлення демонстраційного майстер-секрету та солі */
    memset(ctx->master_secret, 0x4A, 16);
    memset(ctx->master_salt, 0x1F, 8);
    
    ctx->sender_id[0] = 0x01;
    ctx->recipient_id[0] = 0x02;
    ctx->sequence_number = 1;

    /* Виведення ключа відправника та одержувача */
    oscore_derive_key(ctx->master_secret, ctx->master_salt, "SenderKey", ctx->sender_key, 16);
    oscore_derive_key(ctx->master_secret, ctx->master_salt, "RecipientKey", ctx->recipient_key, 16);
    oscore_derive_key(ctx->master_secret, ctx->master_salt, "CommonIV", ctx->common_iv, 13);

    printf("[OSCORE Context] Контекст успішно ініціалізовано. Ключі виведено.\n");
    return 0;
}
