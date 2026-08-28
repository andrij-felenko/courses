#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <math.h>
#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <openssl/crypto.h>

/**
 * Валідація підпису вебхука HMAC-SHA256 мовою C з OpenSSL.
 * Забезпечує порівняння сталого часу через CRYPTO_memcmp та перевірку time-window.
 */
int verify_webhook_hmac(
    const unsigned char *raw_body,
    size_t body_len,
    const char *sig_header,
    const char *primary_secret,
    const char *secondary_secret,
    int tolerance_seconds
) {
    if (!raw_body || !sig_header || !primary_secret) return 0;

    long long timestamp = -1;
    char received_sig[128] = {0};

    /* Парсинг заголовка вигляду: t=1719580800,v1=5257a869e... */
    const char *t_ptr = strstr(sig_header, "t=");
    const char *v1_ptr = strstr(sig_header, "v1=");
    if (!t_ptr || !v1_ptr) return 0;

    if (sscanf(t_ptr, "t=%lld", &timestamp) != 1) return 0;
    if (sscanf(v1_ptr, "v1=%127[^, \t\r\n]", received_sig) != 1) return 0;

    /* 1. Перевірка часового вікна */
    time_t now = time(NULL);
    if (llabs((long long)now - timestamp) > (long long)tolerance_seconds) {
        return 0; /* Запит застарів або з майбутнього */
    }

    /* 2. Складання буфера timestamp.raw_body */
    char t_str[32];
    int t_len = snprintf(t_str, sizeof(t_str), "%lld.", timestamp);
    if (t_len <= 0) return 0;

    size_t sign_data_len = (size_t)t_len + body_len;
    unsigned char *sign_data = (unsigned char *)malloc(sign_data_len);
    if (!sign_data) return 0;

    memcpy(sign_data, t_str, (size_t)t_len);
    memcpy(sign_data + t_len, raw_body, body_len);

    const char *secrets[2] = { primary_secret, secondary_secret };
    int verified = 0;

    /* 3. Перевірка для primary та secondary секретів (ротація) */
    for (int i = 0; i < 2; i++) {
        if (!secrets[i] || strlen(secrets[i]) == 0) continue;

        unsigned char hmac_res[SHA256_DIGEST_LENGTH];
        unsigned int hmac_len = 0;

        HMAC(EVP_sha256(),
             secrets[i], (int)strlen(secrets[i]),
             sign_data, sign_data_len,
             hmac_res, &hmac_len);

        char expected_hex[SHA256_DIGEST_LENGTH * 2 + 1];
        for (unsigned int j = 0; j < hmac_len; j++) {
            snprintf(expected_hex + (j * 2), 3, "%02x", hmac_res[j]);
        }
        expected_hex[SHA256_DIGEST_LENGTH * 2] = '\0';

        /* 4. Безпечне порівняння сталого часу через OpenSSL CRYPTO_memcmp */
        if (strlen(received_sig) == strlen(expected_hex)) {
            if (CRYPTO_memcmp(received_sig, expected_hex, strlen(expected_hex)) == 0) {
                verified = 1;
                break;
            }
        }
    }

    free(sign_data);
    return verified;
}
