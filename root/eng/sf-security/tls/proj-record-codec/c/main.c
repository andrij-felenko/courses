#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <openssl/evp.h>
#include <openssl/err.h>

#define TLS_RECORD_HEADER_LEN   5
#define TLS_AEAD_TAG_LEN        16
#define TLS_MAX_PLAINTEXT_LEN   16384
#define TLS_MAX_RECORD_LEN      (TLS_RECORD_HEADER_LEN + TLS_MAX_PLAINTEXT_LEN + 256 + TLS_AEAD_TAG_LEN)

#define CONTENT_TYPE_INVALID    0
#define CONTENT_TYPE_CCS        20
#define CONTENT_TYPE_ALERT      21
#define CONTENT_TYPE_HANDSHAKE  22
#define CONTENT_TYPE_APPDATA    23

typedef struct {
    uint8_t key[16];        /* 128-бітний ключ AES */
    uint8_t iv[12];         /* 96-бітний статичний вектор ініціалізації */
    uint64_t seq_num;       /* 64-бітний лічильник послідовності */
    EVP_CIPHER_CTX *ctx;
} tls_record_context_t;

int tls_context_init(tls_record_context_t *ctx, const uint8_t key[16], const uint8_t iv[12]) {
    if (!ctx) return -1;
    memcpy(ctx->key, key, 16);
    memcpy(ctx->iv, iv, 12);
    ctx->seq_num = 0;
    ctx->ctx = EVP_CIPHER_CTX_new();
    return (ctx->ctx != NULL) ? 0 : -1;
}

void tls_context_free(tls_record_context_t *ctx) {
    if (ctx && ctx->ctx) {
        EVP_CIPHER_CTX_free(ctx->ctx);
        ctx->ctx = NULL;
    }
}

/* Формування 96-бітного Nonce шляхом XOR статичного IV та 64-бітного лічильника */
static void make_nonce(const uint8_t iv[12], uint64_t seq_num, uint8_t nonce[12]) {
    memcpy(nonce, iv, 12);
    for (int i = 0; i < 8; ++i) {
        nonce[12 - 1 - i] ^= (uint8_t)((seq_num >> (i * 8)) & 0xFF);
    }
}

/* Захист і формування зашифрованого кадру запису (TLS Protect) */
int tls_record_protect(tls_record_context_t *ctx,
                       uint8_t inner_type,
                       const uint8_t *plaintext, size_t plaintext_len,
                       size_t padding_len,
                       uint8_t *out_record, size_t *out_record_len) {
    if (plaintext_len + 1 + padding_len > TLS_MAX_PLAINTEXT_LEN + 256) {
        return -1; /* Перевищення ліміту буфера */
    }

    uint8_t nonce[12];
    make_nonce(ctx->iv, ctx->seq_num, nonce);

    /* 1. Формування буфера відкритого тексту (Payload || InnerType || ZeroPadding) */
    size_t inner_len = plaintext_len + 1 + padding_len;
    uint8_t *inner_buf = (uint8_t *)malloc(inner_len);
    if (!inner_buf) return -1;

    memcpy(inner_buf, plaintext, plaintext_len);
    inner_buf[plaintext_len] = inner_type;
    if (padding_len > 0) {
        memset(inner_buf + plaintext_len + 1, 0x00, padding_len);
    }

    /* 2. Формування 5-байтного зовнішнього заголовка запису */
    size_t ciphertext_len = inner_len + TLS_AEAD_TAG_LEN;
    out_record[0] = 0x17; /* opaque_type: application_data */
    out_record[1] = 0x03; /* legacy_record_version: 0x0303 (TLS 1.2) */
    out_record[2] = 0x03;
    out_record[3] = (uint8_t)((ciphertext_len >> 8) & 0xFF);
    out_record[4] = (uint8_t)(ciphertext_len & 0xFF);

    /* 3. Шифрування AES-128-GCM */
    int len = 0;
    if (EVP_EncryptInit_ex(ctx->ctx, EVP_aes_128_gcm(), NULL, NULL, NULL) != 1 ||
        EVP_CIPHER_CTX_ctrl(ctx->ctx, EVP_CTRL_GCM_SET_IVLEN, 12, NULL) != 1 ||
        EVP_EncryptInit_ex(ctx->ctx, NULL, NULL, ctx->key, nonce) != 1) {
        free(inner_buf);
        return -1;
    }

    /* Аутентифікація додаткових асоційованих даних (AAD = 5 байтів заголовка) */
    if (EVP_EncryptUpdate(ctx->ctx, NULL, &len, out_record, TLS_RECORD_HEADER_LEN) != 1 ||
        EVP_EncryptUpdate(ctx->ctx, out_record + TLS_RECORD_HEADER_LEN, &len, inner_buf, (int)inner_len) != 1) {
        free(inner_buf);
        return -1;
    }

    if (EVP_EncryptFinal_ex(ctx->ctx, out_record + TLS_RECORD_HEADER_LEN + len, &len) != 1) {
        free(inner_buf);
        return -1;
    }

    /* Отримання 16-байтного тегу автентичності */
    uint8_t tag[TLS_AEAD_TAG_LEN];
    if (EVP_CIPHER_CTX_ctrl(ctx->ctx, EVP_CTRL_GCM_GET_TAG, TLS_AEAD_TAG_LEN, tag) != 1) {
        free(inner_buf);
        return -1;
    }
    memcpy(out_record + TLS_RECORD_HEADER_LEN + inner_len, tag, TLS_AEAD_TAG_LEN);

    *out_record_len = TLS_RECORD_HEADER_LEN + ciphertext_len;
    ctx->seq_num++; /* Строгий інкремент лічильника після кожного запису */

    free(inner_buf);
    return 0;
}

/* Розшифрування, перевірка тегу та видалення набивки (TLS Unprotect) */
int tls_record_unprotect(tls_record_context_t *ctx,
                         const uint8_t *record, size_t record_len,
                         uint8_t *out_plaintext, size_t *out_plaintext_len,
                         uint8_t *out_inner_type) {
    if (record_len < TLS_RECORD_HEADER_LEN + TLS_AEAD_TAG_LEN + 1) return -1;

    /* Валідація зовнішнього заголовка */
    if (record[0] != 0x17 || record[1] != 0x03 || record[2] != 0x03) {
        return -1; /* Невірний тип або версія кадру */
    }

    uint16_t wire_len = (uint16_t)((record[3] << 8) | record[4]);
    if (wire_len != record_len - TLS_RECORD_HEADER_LEN) {
        return -1; /* Невідповідність розміру кадру */
    }

    size_t encrypted_payload_len = wire_len - TLS_AEAD_TAG_LEN;
    const uint8_t *tag = record + TLS_RECORD_HEADER_LEN + encrypted_payload_len;

    uint8_t nonce[12];
    make_nonce(ctx->iv, ctx->seq_num, nonce);

    if (EVP_DecryptInit_ex(ctx->ctx, EVP_aes_128_gcm(), NULL, NULL, NULL) != 1 ||
        EVP_CIPHER_CTX_ctrl(ctx->ctx, EVP_CTRL_GCM_SET_IVLEN, 12, NULL) != 1 ||
        EVP_DecryptInit_ex(ctx->ctx, NULL, NULL, ctx->key, nonce) != 1) {
        return -1;
    }

    int len = 0;
    /* Подача AAD (зовнішній заголовок) */
    if (EVP_DecryptUpdate(ctx->ctx, NULL, &len, record, TLS_RECORD_HEADER_LEN) != 1 ||
        EVP_DecryptUpdate(ctx->ctx, out_plaintext, &len, record + TLS_RECORD_HEADER_LEN, (int)encrypted_payload_len) != 1) {
        return -1;
    }

    /* Встановлення очікуваного тегу автентичності */
    if (EVP_CIPHER_CTX_ctrl(ctx->ctx, EVP_CTRL_GCM_SET_TAG, TLS_AEAD_TAG_LEN, (void *)tag) != 1) {
        return -1;
    }

    /* Фінальна перевірка цілісності AEAD */
    if (EVP_DecryptFinal_ex(ctx->ctx, out_plaintext + len, &len) != 1) {
        return -2; /* Фатальна помилка: bad_record_mac / підробка шифротексту */
    }

    /* Пошук InnerContentType: сканування нульової набивки з кінця буфера */
    size_t idx = encrypted_payload_len;
    while (idx > 0 && out_plaintext[idx - 1] == 0x00) {
        idx--;
    }

    if (idx == 0) {
        return -1; /* Помилка: запис складався лише з нулів без типу вмісту */
    }

    *out_inner_type = out_plaintext[idx - 1];
    *out_plaintext_len = idx - 1;

    ctx->seq_num++; /* Інкремент лічильника лише після успішної автентифікації */
    return 0;
}
