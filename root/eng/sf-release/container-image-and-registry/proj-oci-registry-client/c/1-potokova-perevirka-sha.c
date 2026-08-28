#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <openssl/sha.h>
#include <sys/stat.h>
#include <sys/types.h>
#include <unistd.h>

#define BUFFER_SIZE 65536

typedef struct {
    SHA256_CTX ctx;
    unsigned char hash[SHA256_DIGEST_LENGTH];
    char hex_digest[SHA256_DIGEST_LENGTH * 2 + 1];
    size_t total_bytes;
} LayerVerifier;

/* Ініціалізація криптографічного контексту */
void verifier_init(LayerVerifier *v) {
    SHA256_Init(&v->ctx);
    v->total_bytes = 0;
    memset(v->hex_digest, 0, sizeof(v->hex_digest));
}

/* Оновлення контексту при отриманні чергового мережевого чанка */
void verifier_update(LayerVerifier *v, const void *data, size_t len) {
    SHA256_Update(&v->ctx, data, len);
    v->total_bytes += len;
}

/* Фіналізація та звірка з очікуваним дайджестом із маніфесту */
int verifier_finalize_and_check(LayerVerifier *v, const char *expected_digest) {
    SHA256_Final(v->hash, &v->ctx);
    for (int i = 0; i < SHA256_DIGEST_LENGTH; i++) {
        sprintf(&v->hex_digest[i * 2], "%02x", v->hash[i]);
    }
    v->hex_digest[SHA256_DIGEST_LENGTH * 2] = '\0';

    const char *expected_hex = expected_digest;
    if (strncmp(expected_digest, "sha256:", 7) == 0) {
        expected_hex += 7;
    }

    if (strcmp(v->hex_digest, expected_hex) == 0) {
        return 1; /* Хеш валідний: цілісність підтверджено */
    }
    return 0; /* Невідповідність контрольної суми */
}
