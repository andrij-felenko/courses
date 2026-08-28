/* Застарілий підхід OpenSSL 1.1.1 (deprecated у 3.0) */
#include <openssl/hmac.h>

void legacy_openssl_hmac(const unsigned char *key, int key_len,
                         const unsigned char *data, size_t data_len,
                         unsigned char *out_mac, unsigned int *out_len)
{
    HMAC_CTX *ctx = HMAC_CTX_new();
    HMAC_Init_ex(ctx, key, key_len, EVP_sha256(), NULL);
    HMAC_Update(ctx, data, data_len);
    HMAC_Final(ctx, out_mac, out_len);
    HMAC_CTX_free(ctx);
}
