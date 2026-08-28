#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <time.h>
#include <openssl/hmac.h>
#include <openssl/evp.h>
#include <openssl/bio.h>
#include <openssl/buffer.h>

#define MAX_TOKEN_LEN 512
#define HMAC_SHA256_LEN 32

typedef struct {
    char customer_id[64];
    char event_id[64];
    long long exp;
    int valid_parse;
} token_payload_t;

/* Порівняння масивів у константному часі для захисту від Timing Attacks */
static int constant_time_compare(const unsigned char *a, const unsigned char *b, size_t len) {
    unsigned char result = 0;
    for (size_t i = 0; i < len; i++) {
        result |= (a[i] ^ b[i]);
    }
    return result == 0;
}

/* Base64URL декодування */
static int base64url_decode(const char *input, size_t input_len, unsigned char *output, size_t *out_len) {
    BIO *bio, *b64;
    size_t decode_len = input_len;
    char *padded_input = (char *)malloc(input_len + 4);
    if (!padded_input) return -1;

    memcpy(padded_input, input, input_len);
    for (size_t i = 0; i < input_len; i++) {
        if (padded_input[i] == '-') padded_input[i] = '+';
        if (padded_input[i] == '_') padded_input[i] = '/';
    }
    while (decode_len % 4 != 0) {
        padded_input[decode_len++] = '=';
    }
    padded_input[decode_len] = '\0';

    bio = BIO_new_mem_buf(padded_input, (int)decode_len);
    b64 = BIO_new(BIO_f_base64());
    bio = BIO_push(b64, bio);
    BIO_set_flags(bio, BIO_FLAGS_BASE64_NO_NL);

    int decoded_bytes = BIO_read(bio, output, (int)input_len);
    BIO_free_all(bio);
    free(padded_input);

    if (decoded_bytes < 0) return -1;
    *out_len = (size_t)decoded_bytes;
    return 0;
}

/* Розбір payload (формат: customer_id:event_id:exp) */
static token_payload_t parse_payload(const char *payload_str) {
    token_payload_t res;
    memset(&res, 0, sizeof(res));
    
    char buf[256];
    strncpy(buf, payload_str, sizeof(buf) - 1);
    buf[sizeof(buf) - 1] = '\0';

    char *token = strtok(buf, ":");
    if (!token) return res;
    strncpy(res.customer_id, token, sizeof(res.customer_id) - 1);

    token = strtok(NULL, ":");
    if (!token) return res;
    strncpy(res.event_id, token, sizeof(res.event_id) - 1);

    token = strtok(NULL, ":");
    if (!token) return res;
    res.exp = atoll(token);
    res.valid_parse = 1;

    return res;
}

/* Головна функція валідації токену Gatekeeper */
int validate_waiting_room_token(const char *token_str, const char *secret_key, const char *expected_event_id) {
    if (!token_str || !secret_key || !expected_event_id) return 0;

    const char *dot = strchr(token_str, '.');
    if (!dot) return 0;

    size_t payload_len = dot - token_str;
    const char *sig_str = dot + 1;

    if (payload_len == 0 || strlen(sig_str) == 0) return 0;

    char payload_b64[256];
    if (payload_len >= sizeof(payload_b64)) return 0;
    memcpy(payload_b64, token_str, payload_len);
    payload_b64[payload_len] = '\0';

    /* 1. Декодування payload */
    unsigned char decoded_payload[256];
    size_t decoded_payload_len = 0;
    if (base64url_decode(payload_b64, payload_len, decoded_payload, &decoded_payload_len) != 0) {
        return 0;
    }
    decoded_payload[decoded_payload_len] = '\0';

    /* 2. Обчислення очікуваного HMAC-SHA256 підпису */
    unsigned char expected_hmac[EVP_MAX_MD_SIZE];
    unsigned int hmac_len = 0;

    HMAC(EVP_sha256(), secret_key, (int)strlen(secret_key),
         (const unsigned char *)payload_b64, payload_len,
         expected_hmac, &hmac_len);

    /* 3. Декодування переданого підпису */
    unsigned char provided_hmac[64];
    size_t provided_hmac_len = 0;
    if (base64url_decode(sig_str, strlen(sig_str), provided_hmac, &provided_hmac_len) != 0) {
        return 0;
    }

    if (provided_hmac_len != hmac_len) return 0;

    /* 4. Константне порівняння HMAC підписів */
    if (!constant_time_compare(expected_hmac, provided_hmac, hmac_len)) {
        return 0;
    }

    /* 5. Перевірка семантики payload (event_id та exp timestamp) */
    token_payload_t payload = parse_payload((const char *)decoded_payload);
    if (!payload.valid_parse) return 0;

    if (strcmp(payload.event_id, expected_event_id) != 0) {
        return 0;
    }

    long long current_time = (long long)time(NULL);
    if (current_time > payload.exp) {
        return 0; /* Токен прострочено */
    }

    return 1; /* Токен валідний, прохід дозволено */
}
