#include <openssl/hmac.h>
#include <openssl/sha.h>
#include <openssl/crypto.h>
#include <string.h>
#include <stdint.h>
#include <stdbool.h>

#define SHA256_DIGEST_LEN 32

/*
 * HKDF-Extract(salt, ikm) -> prk
 */
bool hkdf_extract_sha256(const uint8_t *salt, size_t salt_len,
                         const uint8_t *ikm, size_t ikm_len,
                         uint8_t prk_out[SHA256_DIGEST_LEN])
{
    uint8_t default_salt[SHA256_DIGEST_LEN] = {0};
    const uint8_t *actual_salt = salt;
    size_t actual_salt_len = salt_len;

    if (actual_salt == NULL || actual_salt_len == 0) {
        actual_salt = default_salt;
        actual_salt_len = sizeof(default_salt);
    }

    unsigned int out_len = 0;
    uint8_t *res = HMAC(EVP_sha256(),
                        actual_salt, (int)actual_salt_len,
                        ikm, ikm_len,
                        prk_out, &out_len);

    return (res != NULL && out_len == SHA256_DIGEST_LEN);
}

/*
 * HKDF-Expand(prk, info, okm_len) -> okm
 */
bool hkdf_expand_sha256(const uint8_t prk[SHA256_DIGEST_LEN],
                        const uint8_t *info, size_t info_len,
                        uint8_t *okm_out, size_t okm_len)
{
    if (okm_out == NULL || okm_len == 0) return false;
    if (okm_len > 255 * SHA256_DIGEST_LEN) return false;

    size_t n = (okm_len + SHA256_DIGEST_LEN - 1) / SHA256_DIGEST_LEN;
    uint8_t t_block[SHA256_DIGEST_LEN];
    size_t t_len = 0;
    size_t bytes_copied = 0;

    HMAC_CTX *ctx = HMAC_CTX_new();
    if (!ctx) return false;

    for (uint8_t i = 1; i <= (uint8_t)n; ++i) {
        if (!HMAC_Init_ex(ctx, prk, SHA256_DIGEST_LEN, EVP_sha256(), NULL)) {
            HMAC_CTX_free(ctx);
            OPENSSL_cleanse(t_block, sizeof(t_block));
            return false;
        }

        if (t_len > 0) {
            HMAC_Update(ctx, t_block, t_len);
        }
        if (info != NULL && info_len > 0) {
            HMAC_Update(ctx, info, info_len);
        }
        HMAC_Update(ctx, &i, 1);

        unsigned int written = 0;
        HMAC_Final(ctx, t_block, &written);
        t_len = written;

        size_t to_copy = (okm_len - bytes_copied < SHA256_DIGEST_LEN)
                         ? (okm_len - bytes_copied)
                         : SHA256_DIGEST_LEN;

        memcpy(okm_out + bytes_copied, t_block, to_copy);
        bytes_copied += to_copy;
    }

    HMAC_CTX_free(ctx);
    OPENSSL_cleanse(t_block, sizeof(t_block));
    return true;
}
