#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>
#include <openssl/sha.h>

#define CHUNK_SIZE 65536

typedef struct {
    char filename[256];
    char url[512];
    char expected_sha256[65];
} PackageRelease;

/* Нормалізація імені проекту згідно з PEP 503 (чистий C99) */
void normalize_package_name(const char* input, char* output, size_t out_len) {
    size_t in_len = strlen(input);
    size_t j = 0;
    int last_was_dash = 0;

    for (size_t i = 0; i < in_len && j + 1 < out_len; ++i) {
        char c = input[i];
        if (c == '-' || c == '_' || c == '.') {
            if (!last_was_dash && j > 0) {
                output[j++] = '-';
                last_was_dash = 1;
            }
        } else {
            output[j++] = (char)tolower((unsigned char)c);
            last_was_dash = 0;
        }
    }
    if (j > 0 && output[j - 1] == '-') {
        j--;
    }
    output[j] = '\0';
}

/* Потокове обчислення SHA-256 контрольної суми відкритого двійкового файлу */
int verify_file_sha256(FILE* file, const char* expected_hex) {
    SHA256_CTX ctx;
    SHA256_Init(&ctx);

    unsigned char buffer[CHUNK_SIZE];
    size_t bytes_read;

    fseek(file, 0, SEEK_SET);
    while ((bytes_read = fread(buffer, 1, sizeof(buffer), file)) > 0) {
        SHA256_Update(&ctx, buffer, bytes_read);
    }

    unsigned char digest[SHA256_DIGEST_LENGTH];
    SHA256_Final(digest, &ctx);

    char computed_hex[SHA256_DIGEST_LENGTH * 2 + 1];
    for (int i = 0; i < SHA256_DIGEST_LENGTH; ++i) {
        sprintf(computed_hex + (i * 2), "%02x", digest[i]);
    }
    computed_hex[64] = '\0';

    return (strcmp(computed_hex, expected_hex) == 0);
}
